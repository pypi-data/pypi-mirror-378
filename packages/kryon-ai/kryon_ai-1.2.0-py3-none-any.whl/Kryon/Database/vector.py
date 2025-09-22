"""
Vector database memory backend for Kryon agents.

This module provides a vector database memory implementation that stores
memory entries with semantic embeddings for advanced similarity search.
Supports Pinecone, Weaviate, Qdrant, and Chroma.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import hashlib
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .base import BaseMemory


class VectorMemory(BaseMemory):
    """
    Vector database memory implementation with semantic search.
    
    Stores memory entries as vectors using embeddings for semantic similarity search.
    Supports multiple vector database backends (Pinecone, Chroma, etc.).
    """
    
    def __init__(self, 
                 provider: str = "chroma",
                 embedding_model: str = "text-embedding-ada-002",
                 **config):
        """
        Initialize vector memory backend.
        
        Args:
            provider: Vector database provider ("pinecone", "chroma", "qdrant", "weaviate")
            embedding_model: OpenAI embedding model to use
            **config: Provider-specific configuration
        """
        self.provider = provider.lower()
        self.embedding_model = embedding_model
        self.client = None
        self.index = None
        self.collection = None
        
        # Provider-specific config
        self.config.update(config)
        
        super().__init__(provider=provider, embedding_model=embedding_model, **config)
    
    def _initialize_backend(self) -> None:
        """Initialize the vector database connection."""
        if self.provider == "pinecone":
            self._initialize_pinecone()
        elif self.provider == "chroma":
            self._initialize_chroma()
        elif self.provider == "qdrant":
            self._initialize_qdrant()
        elif self.provider == "weaviate":
            self._initialize_weaviate()
        else:
            raise ValueError(f"Unsupported vector provider: {self.provider}")
    
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone connection."""
        if not PINECONE_AVAILABLE:
            raise ImportError("pinecone-client is required. Install with: pip install pinecone-client")
        
        api_key = self.config.get("api_key")
        environment = self.config.get("environment", "us-west1-gcp-free")
        index_name = self.config.get("index_name", "kryon-memory")
        
        if not api_key:
            raise ValueError("Pinecone API key is required")
        
        pinecone.init(api_key=api_key, environment=environment)
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=1536,  # OpenAI ada-002 dimension
                metric="cosine"
            )
        
        self.index = pinecone.Index(index_name)
# Connected to Pinecone index
    
    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB connection."""
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")
        
        persist_directory = self.config.get("persist_directory", "./chroma_db")
        collection_name = self.config.get("collection_name", "kryon_memory")
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
# Connected to ChromaDB collection
    
    def _initialize_qdrant(self) -> None:
        """Initialize Qdrant connection (stub implementation)."""
        # This would require qdrant-client
        raise NotImplementedError("Qdrant support not yet implemented")
    
    def _initialize_weaviate(self) -> None:
        """Initialize Weaviate connection (stub implementation)."""
        # This would require weaviate-client
        raise NotImplementedError("Weaviate support not yet implemented")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required for embeddings. Install with: pip install openai")
        
        try:
            client = openai.OpenAI(api_key=self.config.get("openai_api_key"))
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:

            return []
    
    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for content."""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()
    
    def add(self, content: str, entry_type: str = "general", 
            priority: str = "normal", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory entry to the vector database.
        
        Args:
            content: The content to store
            entry_type: Type of entry (task, result, decision, error, etc.)
            priority: Priority level (low, normal, high, critical)
            metadata: Additional metadata to store with the entry
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            # Get embedding for content
            embedding = self._get_embedding(content)
            if not embedding:
                return False
            
            # Create entry
            entry = self.create_entry(content, entry_type, priority, metadata)
            entry_id = self._generate_id(content)
            
            if self.provider == "pinecone":
                return self._add_to_pinecone(entry_id, embedding, entry)
            elif self.provider == "chroma":
                return self._add_to_chroma(entry_id, embedding, entry)
            else:
                return False
                
        except Exception as e:

            return False
    
    def _add_to_pinecone(self, entry_id: str, embedding: List[float], entry: Dict[str, Any]) -> bool:
        """Add entry to Pinecone index."""
        try:
            self.index.upsert([(entry_id, embedding, entry)])
            return True
        except Exception as e:

            return False
    
    def _add_to_chroma(self, entry_id: str, embedding: List[float], entry: Dict[str, Any]) -> bool:
        """Add entry to ChromaDB collection."""
        try:
            self.collection.add(
                ids=[entry_id],
                embeddings=[embedding],
                documents=[entry["content"]],
                metadatas=[{
                    "type": entry["type"],
                    "priority": entry["priority"],
                    "timestamp": entry["timestamp"],
                    "metadata": json.dumps(entry["metadata"])
                }]
            )
            return True
        except Exception as e:

            return False
    
    def get_context_for_task(self, task: str, max_entries: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using semantic similarity.
        
        Args:
            task: The task to get context for
            max_entries: Maximum number of entries to return
            
        Returns:
            List of memory entries relevant to the task
        """
        try:
            # Get embedding for the task
            query_embedding = self._get_embedding(task)
            if not query_embedding:
                return []
            
            if self.provider == "pinecone":
                return self._query_pinecone(query_embedding, max_entries)
            elif self.provider == "chroma":
                return self._query_chroma(query_embedding, max_entries)
            else:
                return []
                
        except Exception as e:

            return []
    
    def _query_pinecone(self, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Query Pinecone for similar vectors."""
        try:
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [match["metadata"] for match in results["matches"]]
        except Exception as e:

            return []
    
    def _query_chroma(self, embedding: List[float], n_results: int) -> List[Dict[str, Any]]:
        """Query ChromaDB for similar vectors."""
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                include=["documents", "metadatas"]
            )
            
            entries = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                entry = {
                    "content": doc,
                    "type": metadata.get("type"),
                    "priority": metadata.get("priority"),
                    "timestamp": metadata.get("timestamp"),
                    "metadata": json.loads(metadata.get("metadata", "{}"))
                }
                entries.append(entry)
            
            return entries
        except Exception as e:

            return []
    
    def get_by_type(self, entry_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve entries by type (limited support in vector databases).
        
        Args:
            entry_type: Type of entries to retrieve
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries of the specified type
        """
        try:
            if self.provider == "chroma":
                results = self.collection.get(
                    where={"type": entry_type},
                    limit=limit,
                    include=["documents", "metadatas"]
                )
                
                entries = []
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i]
                    entry = {
                        "content": doc,
                        "type": metadata.get("type"),
                        "priority": metadata.get("priority"),
                        "timestamp": metadata.get("timestamp"),
                        "metadata": json.loads(metadata.get("metadata", "{}"))
                    }
                    entries.append(entry)
                
                return entries
            else:
                # Pinecone doesn't support metadata filtering in free tier

                return []
        except Exception as e:

            return []
    
    def search_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search content using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory entries
        """
        # Same as get_context_for_task for vector databases
        return self.get_context_for_task(query, limit)
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about the vector database.
        
        Returns:
            Dict containing analytics information
        """
        try:
            if self.provider == "chroma":
                count = self.collection.count()
                return {
                    'backend': 'VectorMemory',
                    'provider': self.provider,
                    'embedding_model': self.embedding_model,
                    'total_entries': count,
                    'collection_name': self.collection.name
                }
            elif self.provider == "pinecone":
                stats = self.index.describe_index_stats()
                return {
                    'backend': 'VectorMemory',
                    'provider': self.provider,
                    'embedding_model': self.embedding_model,
                    'total_entries': stats.get('total_vector_count', 0),
                    'index_name': self.config.get("index_name")
                }
            else:
                return {'backend': 'VectorMemory', 'provider': self.provider}
        except Exception as e:

            return {'error': str(e)}
    
    def clear(self) -> bool:
        """
        Clear all memory entries from the vector database.
        
        Returns:
            bool: True if successfully cleared, False otherwise
        """
        try:
            if self.provider == "chroma":
                # Delete and recreate collection
                collection_name = self.collection.name
                self.client.delete_collection(collection_name)
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                return True
            elif self.provider == "pinecone":
                # Delete all vectors (this can be expensive)
                self.index.delete(delete_all=True)
                return True
            else:
                return False
        except Exception as e:

            return False
