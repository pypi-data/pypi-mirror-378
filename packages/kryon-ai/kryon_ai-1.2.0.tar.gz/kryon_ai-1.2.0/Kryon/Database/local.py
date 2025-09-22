"""
Local JSON file-based database backend for Kryon agents.

This module provides a simple file-based database implementation that stores
memory entries as JSON documents in a local file system.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import BaseMemory


class LocalMemory(BaseMemory):
    """
    Local JSON file-based database implementation.
    
    Stores memory entries in a JSON file on the local filesystem.
    Provides fast read/write access and persistence across agent sessions.
    """
    
    def __init__(self, file_path: str = "agent_memory.json", max_entries: int = 1000, **config):
        """
        Initialize local file-based database.
        
        Args:
            file_path: Path to the JSON memory file
            max_entries: Maximum number of entries to keep in memory
            **config: Additional configuration parameters
        """
        self.file_path = file_path
        self.max_entries = max_entries
        self.memory_data: List[Dict[str, Any]] = []
        super().__init__(file_path=file_path, max_entries=max_entries, **config)
    
    def _initialize_backend(self) -> None:
        """Initialize the local file backend by loading existing data."""
        self._load_from_file()
    
    def _load_from_file(self) -> None:
        """Load memory data from the JSON file."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.memory_data = json.load(f)
            else:
                self.memory_data = []
        except (json.JSONDecodeError, IOError):
            self.memory_data = []
    
    def _save_to_file(self) -> bool:
        """Save memory data to the JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def _compact_memory(self) -> None:
        """Remove oldest entries if we exceed max_entries."""
        if len(self.memory_data) > self.max_entries:
            # Sort by timestamp and keep most recent entries
            self.memory_data.sort(key=lambda x: x.get('timestamp', ''))
            self.memory_data = self.memory_data[-self.max_entries:]
    
    def add(self, content: str, entry_type: str = "general", 
            priority: str = "normal", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory entry to the local file.
        
        Args:
            content: The content to store
            entry_type: Type of entry (task, result, decision, error, etc.)
            priority: Priority level (low, normal, high, critical)
            metadata: Additional metadata to store with the entry
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            entry = self.create_entry(content, entry_type, priority, metadata)
            self.memory_data.append(entry)
            
            # Compact memory if needed
            self._compact_memory()
            
            # Save to file
            return self._save_to_file()
        except Exception:
            return False
    
    def get_context_for_task(self, task: str, max_entries: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a given task.
        
        Args:
            task: The task to get context for
            max_entries: Maximum number of entries to return
            
        Returns:
            List of memory entries relevant to the task
        """
        try:
            # Simple keyword-based matching
            task_lower = task.lower()
            relevant_entries = []
            
            # Sort by timestamp (most recent first)
            sorted_entries = sorted(self.memory_data, 
                                  key=lambda x: x.get('timestamp', ''), 
                                  reverse=True)
            
            for entry in sorted_entries:
                content_lower = entry.get('content', '').lower()
                
                # Check for keyword matches
                if any(word in content_lower for word in task_lower.split()):
                    relevant_entries.append(entry)
                
                if len(relevant_entries) >= max_entries:
                    break
            
            return relevant_entries
        except Exception:
            return []
    
    def get_by_type(self, entry_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve entries by type.
        
        Args:
            entry_type: Type of entries to retrieve
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries of the specified type
        """
        try:
            # Filter by type and sort by timestamp (most recent first)
            type_entries = [entry for entry in self.memory_data 
                           if entry.get('type') == entry_type]
            
            type_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return type_entries[:limit]
        except Exception as e:
            
            return []
    
    def search_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memory content by query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory entries
        """
        try:
            query_lower = query.lower()
            matching_entries = []
            
            for entry in self.memory_data:
                content_lower = entry.get('content', '').lower()
                
                # Simple substring matching
                if query_lower in content_lower:
                    matching_entries.append(entry)
            
            # Sort by timestamp (most recent first)
            matching_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return matching_entries[:limit]
        except Exception as e:
            
            return []
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about the local database.
        
        Returns:
            Dict containing analytics information
        """
        try:
            # Count entries by type
            type_counts = {}
            priority_counts = {}
            
            for entry in self.memory_data:
                entry_type = entry.get('type', 'unknown')
                priority = entry.get('priority', 'unknown')
                
                type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                'backend': 'LocalMemory',
                'file_path': self.file_path,
                'total_entries': len(self.memory_data),
                'max_entries': self.max_entries,
                'types': type_counts,
                'priorities': priority_counts,
                'oldest_entry': min((e.get('timestamp', '') for e in self.memory_data), default=None),
                'newest_entry': max((e.get('timestamp', '') for e in self.memory_data), default=None)
            }
        except Exception as e:
            
            return {'error': str(e)}
    
    def clear(self) -> bool:
        """
        Clear all memory entries.
        
        Returns:
            bool: True if successfully cleared, False otherwise
        """
        try:
            self.memory_data = []
            return self._save_to_file()
        except Exception as e:
            
            return False
    
    def __len__(self) -> int:
        """Return the number of entries in memory."""
        return len(self.memory_data)
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get a memory entry by index."""
        return self.memory_data[index]
