"""
MongoDB-based memory backend for Kryon agents.

This module provides a MongoDB-based memory implementation that stores
memory entries as documents in a MongoDB collection.
Requires pymongo package to be installed.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re

try:
    from pymongo import MongoClient, DESCENDING, IndexModel
    from pymongo.errors import PyMongoError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

from .base import BaseMemory


class MongoMemory(BaseMemory):
    """
    MongoDB-based memory implementation.
    
    Stores memory entries as documents in a MongoDB collection.
    Provides scalable storage and powerful querying capabilities.
    """
    
    def __init__(self, uri: str = "mongodb://localhost:27017", 
                 database: str = "kryon_agents", 
                 collection: str = "memory", 
                 max_entries: int = 10000, **config):
        """
        Initialize MongoDB memory backend.
        
        Args:
            uri: MongoDB connection URI
            database: Database name
            collection: Collection name
            max_entries: Maximum number of entries to keep
            **config: Additional configuration parameters
        """
        if not PYMONGO_AVAILABLE:
            raise ImportError(
                "pymongo is required for MongoMemory. Install with: pip install pymongo"
            )
        
        self.uri = uri
        self.database_name = database
        self.collection_name = collection
        self.max_entries = max_entries
        self.client = None
        self.database = None
        self.collection = None
        
        super().__init__(uri=uri, database=database, collection=collection, 
                        max_entries=max_entries, **config)
    
    def _initialize_backend(self) -> None:
        """Initialize MongoDB connection and setup indexes."""
        try:
            self.client = MongoClient(self.uri)
            self.database = self.client[self.database_name]
            self.collection = self.database[self.collection_name]
            
            # Create indexes for better performance
            indexes = [
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("type", 1)]),
                IndexModel([("priority", 1)]),
                IndexModel([("content", "text")])  # Text search index
            ]
            
            self.collection.create_indexes(indexes)
            
            # Test connection
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {self.database_name}.{self.collection_name}")
            
        except PyMongoError as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    
    def _compact_memory(self) -> None:
        """Remove oldest entries if we exceed max_entries."""
        try:
            total_count = self.collection.count_documents({})
            if total_count > self.max_entries:
                # Find entries to remove (oldest ones)
                entries_to_remove = total_count - self.max_entries
                oldest_entries = self.collection.find({}).sort("timestamp", 1).limit(entries_to_remove)
                
                ids_to_remove = [entry["_id"] for entry in oldest_entries]
                self.collection.delete_many({"_id": {"$in": ids_to_remove}})
                
                print(f"Compacted MongoDB memory: removed {entries_to_remove} oldest entries")
        except PyMongoError as e:
            print(f"Error compacting MongoDB memory: {e}")
    
    def add(self, content: str, entry_type: str = "general", 
            priority: str = "normal", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory entry to MongoDB.
        
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
            
            # Convert timestamp to datetime object for MongoDB
            entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
            
            result = self.collection.insert_one(entry)
            
            # Compact memory if needed
            self._compact_memory()
            
            return result.inserted_id is not None
        except PyMongoError as e:
            print(f"Error adding entry to MongoDB: {e}")
            return False
    
    def get_context_for_task(self, task: str, max_entries: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a given task using MongoDB text search.
        
        Args:
            task: The task to get context for
            max_entries: Maximum number of entries to return
            
        Returns:
            List of memory entries relevant to the task
        """
        try:
            # Use MongoDB text search
            results = []
            
            # First try text search if available
            try:
                cursor = self.collection.find(
                    {"$text": {"$search": task}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"}), ("timestamp", -1)]).limit(max_entries)
                
                results = list(cursor)
            except PyMongoError:
                # Fallback to regex search if text index not available
                pattern = "|".join(re.escape(word) for word in task.split())
                cursor = self.collection.find(
                    {"content": {"$regex": pattern, "$options": "i"}}
                ).sort("timestamp", -1).limit(max_entries)
                
                results = list(cursor)
            
            # Convert MongoDB documents to standard format
            for result in results:
                if "_id" in result:
                    del result["_id"]
                if isinstance(result.get("timestamp"), datetime):
                    result["timestamp"] = result["timestamp"].isoformat()
            
            return results
        except PyMongoError as e:
            print(f"Error retrieving context from MongoDB: {e}")
            return []
    
    def get_by_type(self, entry_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve entries by type from MongoDB.
        
        Args:
            entry_type: Type of entries to retrieve
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries of the specified type
        """
        try:
            cursor = self.collection.find(
                {"type": entry_type}
            ).sort("timestamp", -1).limit(limit)
            
            results = list(cursor)
            
            # Convert MongoDB documents to standard format
            for result in results:
                if "_id" in result:
                    del result["_id"]
                if isinstance(result.get("timestamp"), datetime):
                    result["timestamp"] = result["timestamp"].isoformat()
            
            return results
        except PyMongoError as e:
            print(f"Error retrieving entries by type from MongoDB: {e}")
            return []
    
    def search_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memory content using MongoDB text search.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory entries
        """
        try:
            results = []
            
            # Try text search first
            try:
                cursor = self.collection.find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"}), ("timestamp", -1)]).limit(limit)
                
                results = list(cursor)
            except PyMongoError:
                # Fallback to regex search
                cursor = self.collection.find(
                    {"content": {"$regex": re.escape(query), "$options": "i"}}
                ).sort("timestamp", -1).limit(limit)
                
                results = list(cursor)
            
            # Convert MongoDB documents to standard format
            for result in results:
                if "_id" in result:
                    del result["_id"]
                if isinstance(result.get("timestamp"), datetime):
                    result["timestamp"] = result["timestamp"].isoformat()
            
            return results
        except PyMongoError as e:
            print(f"Error searching MongoDB: {e}")
            return []
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about the MongoDB memory collection.
        
        Returns:
            Dict containing analytics information
        """
        try:
            # Aggregation pipeline for analytics
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_count": {"$sum": 1},
                        "types": {"$push": "$type"},
                        "priorities": {"$push": "$priority"},
                        "oldest": {"$min": "$timestamp"},
                        "newest": {"$max": "$timestamp"}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                
                # Count occurrences of each type and priority
                type_counts = {}
                for t in stats.get("types", []):
                    type_counts[t] = type_counts.get(t, 0) + 1
                
                priority_counts = {}
                for p in stats.get("priorities", []):
                    priority_counts[p] = priority_counts.get(p, 0) + 1
                
                return {
                    'backend': 'MongoMemory',
                    'uri': self.uri,
                    'database': self.database_name,
                    'collection': self.collection_name,
                    'total_entries': stats.get("total_count", 0),
                    'max_entries': self.max_entries,
                    'types': type_counts,
                    'priorities': priority_counts,
                    'oldest_entry': stats.get("oldest").isoformat() if stats.get("oldest") else None,
                    'newest_entry': stats.get("newest").isoformat() if stats.get("newest") else None
                }
            else:
                return {
                    'backend': 'MongoMemory',
                    'uri': self.uri,
                    'database': self.database_name,
                    'collection': self.collection_name,
                    'total_entries': 0,
                    'max_entries': self.max_entries,
                    'types': {},
                    'priorities': {}
                }
        except PyMongoError as e:
            print(f"Error getting analytics from MongoDB: {e}")
            return {'error': str(e)}
    
    def clear(self) -> bool:
        """
        Clear all memory entries from MongoDB.
        
        Returns:
            bool: True if successfully cleared, False otherwise
        """
        try:
            result = self.collection.delete_many({})
            return result.acknowledged
        except PyMongoError as e:
            print(f"Error clearing MongoDB memory: {e}")
            return False
    
    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
    
    def __del__(self):
        """Ensure MongoDB connection is closed when object is destroyed."""
        self.close()