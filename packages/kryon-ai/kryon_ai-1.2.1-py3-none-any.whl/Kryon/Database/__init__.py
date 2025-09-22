"""
Multi-database backend system for Kryon agents.

This package provides a flexible database system that supports multiple storage backends:
- LocalMemory: JSON file-based storage
- MongoMemory: MongoDB document storage  
- VectorMemory: Vector database storage with semantic search

The system allows agents to write to multiple backends simultaneously and
intelligently retrieve information based on backend capabilities.
"""

from .base import BaseMemory
from .local import LocalMemory

# Optional imports with graceful fallbacks
try:
    from .mongo import MongoMemory
except ImportError:
    MongoMemory = None

try:
    from .vector import VectorMemory
except ImportError:
    VectorMemory = None

__all__ = ['BaseMemory', 'LocalMemory', 'MongoMemory', 'VectorMemory']