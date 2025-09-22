"""
Example usage of Kryon Agent with multi-backend memory system.

This example demonstrates how to configure and use an agent with multiple
memory backends: Local JSON, MongoDB, and Vector database storage.
"""

import sys
sys.path.append('.')

from Kryon.llms.groq_llm import GroqLLM
from Kryon.core.predefined_tools import search_web, llm_summarize, explain, chat_agent
from Kryon.core.agent import Agent
from Kryon.Database import LocalMemory

# Optional imports with graceful fallbacks
try:
    from Kryon.Database import MongoMemory
    mongo_available = True
except ImportError:
    
    mongo_available = False

try:
    from Kryon.Database import VectorMemory
    vector_available = True
except ImportError:
    
    vector_available = False


def create_local_only_agent():
    """Create an agent with only local memory backend."""
    # Initialize LLM
    llm = GroqLLM()
    
    # Configure local memory
    local_memory = LocalMemory(
        file_path="examples/local_agent_memory.json",
        max_entries=1000
    )
    
    # Create agent with single backend
    agent = Agent(
        name="LocalAgent",
        llm=llm,
        tools=[search_web, llm_summarize, explain, chat_agent],
        tasks=[
            "Search for information about multi-modal AI",
            "Summarize findings"
        ],
        memory_backends={
            "local": local_memory
        }
    )
    
    return agent


def create_multi_backend_agent():
    """Create an agent with multiple memory backends."""
    
    
    # Initialize LLM
    llm = GroqLLM()
    
    # Configure memory backends
    memory_backends = {}
    
    # Always include local memory
    memory_backends["local"] = LocalMemory(
        file_path="examples/multi_agent_memory.json",
        max_entries=500
    )
    
    # Add MongoDB if available
    if mongo_available:
        try:
            memory_backends["mongo"] = MongoMemory(
                uri="mongodb://localhost:27017",
                database="kryon_agents",
                collection="multi_agent_memory",
                max_entries=2000
            )
            
        except Exception as e:
            
    
    # Add Vector memory if available
    if vector_available:
        try:
            memory_backends["vector"] = VectorMemory(
                provider="chroma",
                persist_directory="examples/vector_db",
                collection_name="multi_agent_memory",
                openai_api_key="your-openai-api-key"  # Replace with actual key
            )
            
        except Exception as e:
            
    
    # Create agent
    agent = Agent(
        name="MultiBackendAgent",
        llm=llm,
        tools=[search_web, llm_summarize, explain, chat_agent],
        tasks=[
            "Search for latest developments in quantum computing",
            "Explain quantum supremacy",
            "Summarize the quantum computing information"
        ],
        memory_backends=memory_backends
    )
    
    return agent


def demonstrate_memory_analytics(agent):
    """Demonstrate memory analytics across all backends."""
    
    
    analytics = agent.get_memory_analytics()
    
    for backend_name, stats in analytics.items():
        
        if "error" in stats:
            
        else:
            
            
            if 'types' in stats:
                
            if 'priorities' in stats:
                


def test_memory_backends():
    """Test individual memory backends."""
    
    
    # Test Local Memory
    
    local_mem = LocalMemory(file_path="examples/test_local.json")
    local_mem.add("Test local content", "test", "normal", {"source": "unit_test"})
    results = local_mem.search_content("test")
    
    
    # Test MongoDB if available
    if mongo_available:
        
        try:
            mongo_mem = MongoMemory(
                uri="mongodb://localhost:27017",
                database="kryon_test",
                collection="test_memory"
            )
            mongo_mem.add("Test mongo content", "test", "normal", {"source": "unit_test"})
            results = mongo_mem.search_content("test")
            
        except Exception as e:
            
    
    # Test Vector Memory if available
    if vector_available:
        
        try:
            vector_mem = VectorMemory(
                provider="chroma",
                persist_directory="examples/test_vector",
                collection_name="test_memory",
                openai_api_key="your-openai-api-key"  # Replace with actual key
            )
            vector_mem.add("Test vector content", "test", "normal", {"source": "unit_test"})
            results = vector_mem.search_content("test")
            
        except Exception as e:
            


def main():
    """Main demonstration function."""
    
    print("=" * 50)
    
    # Test individual backends
    test_memory_backends()
    
    # Create and run local-only agent
    local_agent = create_local_only_agent()
    
    
    
    local_results = local_agent.run()
    
    demonstrate_memory_analytics(local_agent)
    
    # Create and run multi-backend agent
    multi_agent = create_multi_backend_agent()
    
    
    
    multi_results = multi_agent.run()
    
    demonstrate_memory_analytics(multi_agent)
    
    # Demonstrate backend management
    
    print("Available backends before removal:", list(multi_agent.memory_backends.keys()))
    
    # Try to remove a backend (if exists)
    if "mongo" in multi_agent.memory_backends:
        multi_agent.remove_memory_backend("mongo")
        print("Available backends after mongo removal:", list(multi_agent.memory_backends.keys()))
    
    # Add a backend dynamically
    new_local = LocalMemory(file_path="examples/dynamic_memory.json")
    multi_agent.add_memory_backend("dynamic_local", new_local)
    print("Available backends after adding dynamic backend:", list(multi_agent.memory_backends.keys()))
    
    
    
    
    
    
    
    


if __name__ == "__main__":
    main()
