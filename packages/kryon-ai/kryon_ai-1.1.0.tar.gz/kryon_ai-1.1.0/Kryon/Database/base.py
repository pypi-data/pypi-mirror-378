"""
Base database interface for Kryon agent database backends.

This module defines the abstract base class that all database backends must implement,
ensuring consistent interface across different storage systems.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseMemory(ABC):
    """
    Abstract base class for agent database backends.
    
    All database implementations must inherit from this class and implement
    the required methods to ensure consistent behavior across different
    storage systems.
    """
    
    def __init__(self, **config):
        """
        Initialize the database backend with configuration parameters.
        
        Args:
            **config: Backend-specific configuration parameters
        """
        self.config = config
        self._initialize_backend()
    
    @abstractmethod
    def _initialize_backend(self) -> None:
        """
        Initialize the backend-specific resources.
        
        This method should handle connection setup, schema creation,
        or any other initialization required for the backend.
        """
        pass
    
    @abstractmethod
    def add(self, content: str, entry_type: str = "general", 
            priority: str = "normal", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory entry to the backend.
        
        Args:
            content: The content to store
            entry_type: Type of entry (task, result, decision, error, etc.)
            priority: Priority level (low, normal, high, critical)
            metadata: Additional metadata to store with the entry
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        pass
    
    @abstractmethod
    def get_context_for_task(self, task: str, max_entries: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a given task.
        
        Args:
            task: The task to get context for
            max_entries: Maximum number of entries to return
            
        Returns:
            List of memory entries relevant to the task
        """
        pass
    
    @abstractmethod
    def get_by_type(self, entry_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve entries by type.
        
        Args:
            entry_type: Type of entries to retrieve
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries of the specified type
        """
        pass
    
    @abstractmethod
    def search_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memory content by query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory entries
        """
        pass
    
    @abstractmethod
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about the database backend.
        
        Returns:
            Dict containing analytics information (entry counts, types, etc.)
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all memory entries.
        
        Returns:
            bool: True if successfully cleared, False otherwise
        """
        pass
    
    def create_entry(self, content: str, entry_type: str = "general", 
                    priority: str = "normal", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a standardized memory entry.
        
        Args:
            content: The content to store
            entry_type: Type of entry
            priority: Priority level
            metadata: Additional metadata
            
        Returns:
            Dict representing the memory entry
        """
        entry = {
            "content": content,
            "type": entry_type,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        return entry
    
    def __repr__(self) -> str:
        """String representation of the database backend."""
        return f"{self.__class__.__name__}(config={self.config})"