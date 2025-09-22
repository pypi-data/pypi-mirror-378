# Kryon/core/memory.py
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class Memory:
    def __init__(self, persistent_file: Optional[str] = None, max_entries: int = 1000):
        # Keep original simple history for backward compatibility
        self.history = []
        
        # Enhanced memory features
        self.enhanced_history: List[Dict[str, Any]] = []
        self.max_entries = max_entries
        self.persistent_file = persistent_file
        
        # Load from file if persistence is enabled
        if self.persistent_file and os.path.exists(self.persistent_file):
            self._load_from_file()

    def add(self, entry: str):
        """Add a new memory entry (backward compatible)"""
        # Keep original functionality
        self.history.append(entry)
        
        # Enhanced functionality with metadata
        enhanced_entry = {
            "content": entry,
            "timestamp": datetime.now().isoformat(),
            "type": "general",
            "context_level": "normal"
        }
        self._add_enhanced_entry(enhanced_entry)

    def add_enhanced(self, entry: str, entry_type: str = "general", 
                    context_level: str = "normal", metadata: Optional[Dict] = None):
        """Add memory entry with enhanced metadata"""
        # Also add to simple history for compatibility
        self.history.append(entry)
        
        enhanced_entry = {
            "content": entry,
            "timestamp": datetime.now().isoformat(),
            "type": entry_type,  # task, result, decision, error, etc.
            "context_level": context_level,  # low, normal, high, critical
            "metadata": metadata or {}
        }
        self._add_enhanced_entry(enhanced_entry)

    def _add_enhanced_entry(self, entry: Dict[str, Any]):
        """Internal method to add enhanced entry with size management"""
        self.enhanced_history.append(entry)
        
        # Manage memory size
        if len(self.enhanced_history) > self.max_entries:
            # Keep recent entries and summarize old ones
            self._compact_old_memories()
            
        # Save to file if persistence is enabled
        if self.persistent_file:
            self._save_to_file()

    def get_all(self):
        """Retrieve all memory entries (backward compatible)"""
        return self.history.copy()

    def get_last(self, n=1):
        """Retrieve last n entries (backward compatible)"""
        return self.history[-n:]

    def get_context_for_task(self, current_task: str = "", max_entries: int = 5) -> str:
        """Get relevant context for current task - NEW METHOD"""
        if not self.enhanced_history:
            return ""
            
        # Get recent high-context entries
        relevant_entries = []
        for entry in reversed(self.enhanced_history):
            if entry["context_level"] in ["high", "critical"]:
                relevant_entries.append(entry)
                if len(relevant_entries) >= max_entries // 2:
                    break
        
        # Fill remaining slots with recent entries
        remaining_slots = max_entries - len(relevant_entries)
        if remaining_slots > 0:
            recent_entries = []
            for entry in reversed(self.enhanced_history):
                if entry not in relevant_entries:
                    recent_entries.append(entry)
                    if len(recent_entries) >= remaining_slots:
                        break
            relevant_entries.extend(recent_entries)
        
        # Format context string
        context_lines = []
        for entry in reversed(relevant_entries):  # Chronological order
            timestamp = entry["timestamp"][:19].replace("T", " ")  # Clean timestamp
            context_lines.append(f"[{timestamp}] {entry['content']}")
            
        return "\n".join(context_lines)

    def get_by_type(self, entry_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get entries by type - NEW METHOD"""
        filtered = [entry for entry in self.enhanced_history if entry["type"] == entry_type]
        return filtered[-limit:]

    def search_content(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory content - NEW METHOD"""
        keyword_lower = keyword.lower()
        matches = []
        for entry in self.enhanced_history:
            if keyword_lower in entry["content"].lower():
                matches.append(entry)
                if len(matches) >= limit:
                    break
        return matches

    def _compact_old_memories(self):
        """Summarize old memories to save space"""
        if len(self.enhanced_history) <= self.max_entries:
            return
            
        # Keep last 70% of entries, summarize the rest
        keep_count = int(self.max_entries * 0.7)
        old_entries = self.enhanced_history[:-keep_count]
        
        # Create summary of old entries
        if old_entries:
            summary_content = f"Summary of {len(old_entries)} previous interactions"
            summary_entry = {
                "content": summary_content,
                "timestamp": datetime.now().isoformat(),
                "type": "summary",
                "context_level": "low",
                "metadata": {"summarized_count": len(old_entries)}
            }
            
            # Keep recent entries + summary
            self.enhanced_history = [summary_entry] + self.enhanced_history[-keep_count:]
            
            # Update simple history too
            summary_start = len(self.history) - len(old_entries)
            self.history = [summary_content] + self.history[summary_start:]

    def _save_to_file(self):
        """Save enhanced history to file"""
        try:
            with open(self.persistent_file, 'w') as f:
                json.dump({
                    "history": self.history,
                    "enhanced_history": self.enhanced_history
                }, f, indent=2)
        except Exception:
            pass  # Fail silently to not break existing functionality

    def _load_from_file(self):
        """Load enhanced history from file"""
        try:
            with open(self.persistent_file, 'r') as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.enhanced_history = data.get("enhanced_history", [])
        except Exception:
            pass  # Fail silently to not break existing functionality

    def clear(self):
        """Clear all memory"""
        self.history = []
        self.enhanced_history = []
        if self.persistent_file and os.path.exists(self.persistent_file):
            os.remove(self.persistent_file)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics - NEW METHOD"""
        types = {}
        for entry in self.enhanced_history:
            entry_type = entry["type"]
            types[entry_type] = types.get(entry_type, 0) + 1
            
        return {
            "total_entries": len(self.enhanced_history),
            "simple_entries": len(self.history),
            "types": types,
            "oldest_entry": self.enhanced_history[0]["timestamp"] if self.enhanced_history else None,
            "newest_entry": self.enhanced_history[-1]["timestamp"] if self.enhanced_history else None
        }
