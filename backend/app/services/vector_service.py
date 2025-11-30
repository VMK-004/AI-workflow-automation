"""Vector service for FAISS integration via LangChain"""
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import pickle

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

logger = logging.getLogger(__name__)


class VectorService:
    """Service for FAISS vector store operations"""
    
    def __init__(self):
        """Initialize vector service"""
        self.base_path = Path("data/faiss")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings model
        self.embeddings = None
        self._initialize_embeddings()
        
        # Cache for loaded indices
        self._index_cache: Dict[str, FAISS] = {}
    
    def _initialize_embeddings(self):
        """Initialize the embeddings model (sentence-transformers)"""
        try:
            logger.info("Loading embeddings model: all-MiniLM-L6-v2")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("Embeddings model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {str(e)}")
            self.embeddings = None
    
    async def create_collection(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a new FAISS collection from documents.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents with 'text' and optional 'metadata'
        
        Returns:
            Dict with collection info
        """
        try:
            if self.embeddings is None:
                raise Exception("Embeddings model not loaded")
            
            # Convert to LangChain Document objects
            docs = [
                Document(
                    page_content=doc.get("text", ""),
                    metadata=doc.get("metadata", {})
                )
                for doc in documents
            ]
            
            # Create FAISS index
            logger.info(f"Creating FAISS collection '{collection_name}' with {len(docs)} documents")
            vectorstore = FAISS.from_documents(docs, self.embeddings)
            
            # Save to disk
            collection_path = self.base_path / collection_name
            vectorstore.save_local(str(collection_path))
            
            # Cache the index
            self._index_cache[collection_name] = vectorstore
            
            logger.info(f"Collection '{collection_name}' created and saved")
            
            return {
                "collection_name": collection_name,
                "document_count": len(docs),
                "path": str(collection_path),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {str(e)}")
            raise
    
    async def load_collection(self, collection_name: str) -> FAISS:
        """
        Load a FAISS collection from disk.
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            FAISS vectorstore object
        """
        # Check cache first
        if collection_name in self._index_cache:
            logger.debug(f"Using cached index for '{collection_name}'")
            return self._index_cache[collection_name]
        
        try:
            if self.embeddings is None:
                raise Exception("Embeddings model not loaded")
            
            collection_path = self.base_path / collection_name
            
            if not collection_path.exists():
                raise FileNotFoundError(f"Collection '{collection_name}' not found at {collection_path}")
            
            logger.info(f"Loading FAISS collection from {collection_path}")
            vectorstore = FAISS.load_local(
                str(collection_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Cache it
            self._index_cache[collection_name] = vectorstore
            
            logger.info(f"Collection '{collection_name}' loaded successfully")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Failed to load collection '{collection_name}': {str(e)}")
            raise
    
    async def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search a FAISS collection.
        
        Args:
            collection_name: Name of the collection to search
            query: Search query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score (optional)
            metadata_filter: Filter by metadata (optional)
        
        Returns:
            Dict with search results
        """
        try:
            # Load or get cached collection
            vectorstore = await self.load_collection(collection_name)
            
            logger.info(f"Searching collection '{collection_name}' with query: {query[:50]}...")
            
            # Perform similarity search with scores
            results = vectorstore.similarity_search_with_score(
                query,
                k=top_k
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                # Apply score threshold if specified
                if score_threshold is not None and score < score_threshold:
                    continue
                
                # Apply metadata filter if specified
                if metadata_filter is not None:
                    match = all(
                        doc.metadata.get(key) == value
                        for key, value in metadata_filter.items()
                    )
                    if not match:
                        continue
                
                formatted_results.append({
                    "text": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            
            return {
                "results": formatted_results,
                "query": query,
                "collection_name": collection_name,
                "total_results": len(formatted_results),
                "top_k": top_k,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Search failed in collection '{collection_name}': {str(e)}")
            raise
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add documents to an existing collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to add
        
        Returns:
            Dict with operation result
        """
        try:
            # Load collection
            vectorstore = await self.load_collection(collection_name)
            
            # Convert to LangChain Documents
            docs = [
                Document(
                    page_content=doc.get("text", ""),
                    metadata=doc.get("metadata", {})
                )
                for doc in documents
            ]
            
            logger.info(f"Adding {len(docs)} documents to collection '{collection_name}'")
            
            # Add documents
            vectorstore.add_documents(docs)
            
            # Save updated index
            collection_path = self.base_path / collection_name
            vectorstore.save_local(str(collection_path))
            
            # Update cache
            self._index_cache[collection_name] = vectorstore
            
            logger.info(f"Added {len(docs)} documents to '{collection_name}'")
            
            return {
                "collection_name": collection_name,
                "documents_added": len(docs),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to add documents to '{collection_name}': {str(e)}")
            raise
    
    async def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete a FAISS collection.
        
        Args:
            collection_name: Name of the collection to delete
        
        Returns:
            Dict with operation result
        """
        try:
            collection_path = self.base_path / collection_name
            
            if collection_path.exists():
                import shutil
                shutil.rmtree(collection_path)
                logger.info(f"Deleted collection '{collection_name}' from disk")
            
            # Remove from cache
            if collection_name in self._index_cache:
                del self._index_cache[collection_name]
            
            return {
                "collection_name": collection_name,
                "status": "deleted"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {str(e)}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all available FAISS collections"""
        try:
            collections = [
                d.name for d in self.base_path.iterdir()
                if d.is_dir()
            ]
            return collections
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            return []
    
    def is_available(self) -> bool:
        """Check if the vector service is available"""
        return self.embeddings is not None


# Singleton instance
_vector_service_instance = None

def get_vector_service() -> VectorService:
    """Get singleton instance of VectorService"""
    global _vector_service_instance
    if _vector_service_instance is None:
        _vector_service_instance = VectorService()
    return _vector_service_instance
