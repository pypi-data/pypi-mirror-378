import inspect
from .memory import Memory
from ..Database import BaseMemory, LocalMemory
from typing import List, Dict, Any, Optional, Union

class Agent:
    """
    Unified Agent class with optional multi-backend memory support.
    
    This class combines the functionality of the original Agent with the 
    multi-backend memory capabilities, making memory backends optional.
    
    Usage:
    - Without memory backends: Agent(name="MyAgent", llm=my_llm, tools=[...])
    - With memory backends: Agent(name="MyAgent", llm=my_llm, tools=[...], 
                                 memory_backends={"local": LocalMemory(), "mongo": MongoMemory()})
    """
    
    def __init__(self, name: str, llm, tools: Optional[List] = None, tasks: Optional[List[str]] = None, 
                 memory_config: Optional[Dict[str, Any]] = None, 
                 memory_backends: Optional[Dict[str, BaseMemory]] = None):
        """
        Initialize Agent with optional memory backends.
        
        Args:
            name: Agent name
            llm: Language model instance
            tools: List of available tools
            tasks: List of tasks to execute
            memory_config: Legacy memory config (for backward compatibility)
            memory_backends: Dict of memory backend instances {"local": LocalMemory(), ...}
        """
        self.name = name
        self.llm = llm
        self.tools = {t.__name__: t for t in (tools or [])}
        self.tasks = tasks or []
        
        # Determine memory mode based on parameters
        self.use_multi_memory = memory_backends is not None
        
        if self.use_multi_memory:
            # Multi-backend memory mode
            self.memory_backends = memory_backends or {}
            
            # Ensure we have at least a local memory backend
            if not self.memory_backends:
                self.memory_backends["local"] = LocalMemory()
            elif "local" not in self.memory_backends:
                self.memory_backends["local"] = LocalMemory()
                
            # Legacy memory is None in multi-backend mode
            self.memory = None
        else:
            # Legacy single memory mode (backward compatible)
            if memory_config:
                self.memory = Memory(
                    persistent_file=memory_config.get("persistent_file"),
                    max_entries=memory_config.get("max_entries", 1000)
                )
            else:
                self.memory = Memory()  # Default behavior unchanged
                
            # No multi-backend support
            self.memory_backends = {}
    
    def add_memory_backend(self, name: str, backend: BaseMemory) -> None:
        """
        Add a memory backend to the agent (only works if multi-memory mode is enabled).
        
        Args:
            name: Backend name identifier
            backend: Memory backend instance
        """
        if not self.use_multi_memory:
            raise RuntimeError("Cannot add memory backends when not in multi-memory mode. "
                             "Initialize Agent with memory_backends parameter.")
        self.memory_backends[name] = backend
    
    def remove_memory_backend(self, name: str) -> bool:
        """
        Remove a memory backend from the agent.
        
        Args:
            name: Backend name identifier
            
        Returns:
            bool: True if removed, False if not found
        """
        if not self.use_multi_memory:
            return False
        if name in self.memory_backends and name != "local":
            del self.memory_backends[name]
            return True
        return False
    
    def _add_to_all_backends(self, content: str, entry_type: str = "general", 
                           priority: str = "normal", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Add memory entry to all configured backends (multi-memory mode only).
        
        Args:
            content: Content to store
            entry_type: Type of entry
            priority: Priority level
            metadata: Additional metadata
            
        Returns:
            Dict mapping backend names to success status
        """
        if not self.use_multi_memory:
            return {}
            
        results = {}
        for backend_name, backend in self.memory_backends.items():
            try:
                results[backend_name] = backend.add(content, entry_type, priority, metadata)
            except Exception:
                results[backend_name] = False
        return results
    
    def _get_context_intelligent(self, task: str, max_entries: int = 5) -> List[Dict[str, Any]]:
        """
        Intelligently retrieve context with fallback strategy (multi-memory mode).
        
        Strategy:
        1. Try vector memory first (best semantic matching)
        2. Fall back to mongo (good search capabilities)
        3. Fall back to local (basic but reliable)
        
        Args:
            task: Task to get context for
            max_entries: Maximum entries to return
            
        Returns:
            List of relevant memory entries
        """
        if not self.use_multi_memory:
            return []
            
        # Try vector memory first (best semantic search)
        if "vector" in self.memory_backends:
            try:
                context = self.memory_backends["vector"].get_context_for_task(task, max_entries)
                if context:
                    return context
            except Exception:
                pass
        
        # Fall back to mongo (good text search)
        if "mongo" in self.memory_backends:
            try:
                context = self.memory_backends["mongo"].get_context_for_task(task, max_entries)
                if context:
                    return context
            except Exception:
                pass
        
        # Fall back to local memory (basic but reliable)
        if "local" in self.memory_backends:
            try:
                return self.memory_backends["local"].get_context_for_task(task, max_entries)
            except Exception:
                pass
        
        return []
    
    def _get_by_type_intelligent(self, entry_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Intelligently retrieve entries by type with fallback (multi-memory mode).
        
        Args:
            entry_type: Type of entries to retrieve
            limit: Maximum number of entries
            
        Returns:
            List of entries of the specified type
        """
        if not self.use_multi_memory:
            return []
            
        # Try mongo first (best for type filtering)
        if "mongo" in self.memory_backends:
            try:
                entries = self.memory_backends["mongo"].get_by_type(entry_type, limit)
                if entries:
                    return entries
            except Exception:
                pass
        
        # Fall back to local
        if "local" in self.memory_backends:
            try:
                return self.memory_backends["local"].get_by_type(entry_type, limit)
            except Exception:
                pass
        
        # Try vector as last resort
        if "vector" in self.memory_backends:
            try:
                return self.memory_backends["vector"].get_by_type(entry_type, limit)
            except Exception:
                pass
        
        return []
    
    def get_memory_analytics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get analytics from memory system.
        
        Returns:
            Dict with memory analytics (format depends on memory mode)
        """
        if self.use_multi_memory:
            analytics = {}
            for backend_name, backend in self.memory_backends.items():
                try:
                    analytics[backend_name] = backend.get_analytics()
                except Exception as e:
                    analytics[backend_name] = {"error": str(e)}
            return analytics
        else:
            # Legacy memory analytics
            if hasattr(self.memory, 'get_analytics'):
                return {"legacy": self.memory.get_analytics()}
            else:
                return {"legacy": {"entries": len(getattr(self.memory, 'memory', []))}}
    
    def clear_all_memory(self) -> Union[Dict[str, bool], bool]:
        """
        Clear memory from all backends or legacy memory.
        
        Returns:
            Dict mapping backend names to clear success status (multi-memory) or 
            bool (legacy memory)
        """
        if self.use_multi_memory:
            results = {}
            for backend_name, backend in self.memory_backends.items():
                try:
                    results[backend_name] = backend.clear()
                except Exception:
                    results[backend_name] = False
            return results
        else:
            # Legacy memory clear
            if hasattr(self.memory, 'clear'):
                self.memory.clear()
                return True
            else:
                self.memory.memory = []
                return True

    def run_task(self, task: str) -> str:
        """
        Execute a task using appropriate memory system.
        
        Args:
            task: Task to execute
            
        Returns:
            str: Task execution result
        """
        # Add task to appropriate memory system
        if self.use_multi_memory:
            self._add_to_all_backends(f"Task: {task}", "task", "high")
            # Get relevant context using intelligent retrieval
            memory_context = self._get_context_intelligent(task, max_entries=3)
            context_text = ""
            if memory_context:
                context_text = "\n".join([f"- {entry['content'][:100]}..." for entry in memory_context])
        else:
            # Legacy memory system
            self.memory.add_enhanced(f"Task: {task}", "task", "high")
            # Get relevant context from legacy memory
            memory_context = self.memory.get_context_for_task(task, max_entries=3)
            context_text = memory_context
        
        # Create tool descriptions for better LLM decision-making
        tool_descriptions = []
        for tool_name in self.tools.keys():
            tool_func = self.tools[tool_name]
            doc = tool_func.__doc__ or "General purpose tool"
            tool_descriptions.append(f"- {tool_name}: {doc.strip()}")
        
        tools_info = "\n".join(tool_descriptions)
        
        # Enhanced decision prompt that encourages tool usage
        if context_text:
            decision_prompt = (
                f"You are an AI agent named {self.name}.\n\n"
                f"Available tools:\n{tools_info}\n\n"
                f"Recent context:\n{context_text}\n\n"
                f"Current task: {task}\n\n"
                f"IMPORTANT: Choose the appropriate tool for this task. Prefer using tools over direct responses.\n\n"
                f"Guidelines:\n"
                f"- For search/research tasks: respond with 'search_web'\n"
                f"- For summarization tasks: respond with 'llm_summarize'\n"
                f"- For explanation tasks: respond with 'explain'\n"
                f"- For chat/conversation tasks: respond with 'chat_agent'\n"
                f"- For other tasks: respond with the best matching tool name\n\n"
                f"DO NOT use function calling syntax. Just respond with the tool name as plain text.\n"
                f"Example responses: 'search_web' or 'llm_summarize' or 'explain'"
            )
        else:
            # Enhanced prompt even without context
            decision_prompt = (
                f"You are an AI agent named {self.name}.\n\n"
                f"Available tools:\n{tools_info}\n\n"
                f"Task: {task}\n\n"
                f"IMPORTANT: Choose the appropriate tool for this task. Prefer using tools over direct responses.\n\n"
                f"Guidelines:\n"
                f"- For search/research tasks: respond with 'search_web'\n"
                f"- For summarization tasks: respond with 'llm_summarize'\n"
                f"- For explanation tasks: respond with 'explain'\n"
                f"- For chat/conversation tasks: respond with 'chat_agent'\n"
                f"- For other tasks: respond with the best matching tool name\n\n"
                f"DO NOT use function calling syntax. Just respond with the tool name as plain text.\n"
                f"Example responses: 'search_web' or 'llm_summarize' or 'explain'"
            )
        
        # Make decision and normalize for better matching
        decision = self.llm.generate(decision_prompt).strip().lower()

        if decision in self.tools:
            tool_func = self.tools[decision]
            sig = inspect.signature(tool_func)

            # Log tool decision using appropriate memory system
            if self.use_multi_memory:
                self._add_to_all_backends(f"Decision: Using tool '{decision}'", "decision", "high")
            else:
                self.memory.add_enhanced(f"Decision: Using tool '{decision}'", "decision", "high")

            try:
                # Prepare the task with context if the LLM decides it's needed
                final_task = task
                
                # Enhanced summarization - always feed past results for better context
                if decision == "llm_summarize":
                    if self.use_multi_memory:
                        past_results = self._get_by_type_intelligent("result", limit=3)
                    else:
                        past_results = self.memory.get_by_type("result", limit=3)
                    
                    if past_results:
                        combined = "\n\n".join(r["content"] for r in past_results)
                        final_task = f"Summarize the following results:\n\n{combined}"
                
                # Execute the tool
                if 'llm' in sig.parameters:
                    result = tool_func(final_task, self.llm)
                elif len(sig.parameters) == 1:
                    result = tool_func(final_task)
                elif len(sig.parameters) == 0:
                    result = tool_func()
                else:
                    raise TypeError(f"Tool {tool_func.__name__} has unsupported signature.")

                # Log successful result using appropriate memory system
                if self.use_multi_memory:
                    self._add_to_all_backends(f"Tool result: {result}", "result", "normal", 
                                            {"tool_used": decision, "success": True})
                else:
                    self.memory.add_enhanced(f"Tool result: {result}", "result", "normal", 
                                           {"tool_used": decision, "success": True})
            except Exception as e:
                error_msg = f"Tool execution error: {str(e)}"
                
                # Log error using appropriate memory system
                if self.use_multi_memory:
                    self._add_to_all_backends(error_msg, "error", "critical", 
                                            {"tool_attempted": decision, "error": str(e)})
                else:
                    self.memory.add_enhanced(error_msg, "error", "critical", 
                                           {"tool_attempted": decision, "error": str(e)})
                result = f"Error executing {decision}: {str(e)}"
        else:
            result = decision
            
            # Log LLM direct response using appropriate memory system
            if self.use_multi_memory:
                self._add_to_all_backends(f"Direct LLM response: {result}", "response", "normal")
            else:
                self.memory.add_enhanced(f"Direct LLM response: {result}", "response", "normal")

        return result

    def run(self) -> List[str]:
        """
        Execute all configured tasks.
        
        Returns:
            List of task results
        """
        results = []
        for task in self.tasks:
            results.append(self.run_task(task))
        return results
