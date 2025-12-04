"""Vector collection service for managing collection metadata in database"""
import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.vector_collection import VectorCollection
from app.services.vector_service import get_vector_service
from app.exceptions import HandlerExecutionError

logger = logging.getLogger(__name__)


class VectorCollectionService:
    """Service for managing vector collections (database + FAISS)"""
    
    @staticmethod
    async def create_collection(
        db: AsyncSession,
        user_id: UUID,
        name: str,
        documents: List[Dict[str, Any]]
    ) -> VectorCollection:
        """
        Create a new vector collection.
        
        Args:
            db: Database session
            user_id: ID of the user creating the collection
            name: Name of the collection
            documents: List of initial documents
        
        Returns:
            Created VectorCollection object
        
        Raises:
            HTTPException: If collection already exists or creation fails
        """
        try:
            # Check if collection already exists for this user
            existing = await VectorCollectionService.get_collection_by_name(
                db, user_id, name
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Collection '{name}' already exists"
                )
            
            logger.info(f"Creating vector collection '{name}' for user {user_id}")
            
            # Create FAISS index using VectorService
            vector_service = get_vector_service()
            
            # Get full collection name (user-scoped)
            full_name = f"{user_id}_{name}"
            
            result = await vector_service.create_collection(
                collection_name=full_name,
                documents=documents
            )
            
            # Get embeddings dimension from vector service
            dimension = 384  # all-MiniLM-L6-v2 default
            
            # Create database record
            collection = VectorCollection(
                user_id=user_id,
                name=name,
                dimension=dimension,
                index_path=result.get("path"),
                document_count=len(documents)
            )
            
            db.add(collection)
            await db.commit()
            await db.refresh(collection)
            
            logger.info(f"Collection '{name}' created with {len(documents)} documents")
            
            return collection
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create collection '{name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create collection: {str(e)}"
            )
    
    @staticmethod
    async def get_collection_by_name(
        db: AsyncSession,
        user_id: UUID,
        name: str
    ) -> Optional[VectorCollection]:
        """
        Get collection by name for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            name: Collection name
        
        Returns:
            VectorCollection or None if not found
        """
        stmt = select(VectorCollection).where(
            VectorCollection.user_id == user_id,
            VectorCollection.name == name
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_collection_by_id(
        db: AsyncSession,
        collection_id: UUID,
        user_id: UUID
    ) -> Optional[VectorCollection]:
        """
        Get collection by ID with user validation.
        
        Args:
            db: Database session
            collection_id: Collection ID
            user_id: User ID for authorization
        
        Returns:
            VectorCollection or None if not found/unauthorized
        """
        stmt = select(VectorCollection).where(
            VectorCollection.id == collection_id,
            VectorCollection.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_collections(
        db: AsyncSession,
        user_id: UUID
    ) -> List[VectorCollection]:
        """
        List all collections for a user.
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            List of VectorCollection objects
        """
        stmt = select(VectorCollection).where(
            VectorCollection.user_id == user_id
        ).order_by(VectorCollection.created_at.desc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def add_documents(
        db: AsyncSession,
        user_id: UUID,
        name: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add documents to an existing collection.
        
        Args:
            db: Database session
            user_id: User ID
            name: Collection name
            documents: List of documents to add
        
        Returns:
            Dict with operation result
        
        Raises:
            HTTPException: If collection not found or operation fails
        """
        try:
            # Get collection from database
            collection = await VectorCollectionService.get_collection_by_name(
                db, user_id, name
            )
            
            if not collection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Collection '{name}' not found"
                )
            
            logger.info(f"Adding {len(documents)} documents to collection '{name}'")
            
            # Add documents to FAISS index
            vector_service = get_vector_service()
            full_name = f"{user_id}_{name}"
            
            result = await vector_service.add_documents(
                collection_name=full_name,
                documents=documents
            )
            
            # Update document count in database
            collection.document_count += len(documents)
            await db.commit()
            await db.refresh(collection)
            
            logger.info(f"Added {len(documents)} documents to '{name}'")
            
            return {
                "collection_name": name,
                "documents_added": len(documents),
                "total_documents": collection.document_count,
                "status": "success"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to add documents to '{name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add documents: {str(e)}"
            )
    
    @staticmethod
    async def search_collection(
        db: AsyncSession,
        user_id: UUID,
        name: str,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search in a collection.
        
        Args:
            db: Database session
            user_id: User ID
            name: Collection name
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            metadata_filter: Filter by metadata
        
        Returns:
            Dict with search results
        
        Raises:
            HTTPException: If collection not found or search fails
        """
        try:
            # Verify collection exists
            collection = await VectorCollectionService.get_collection_by_name(
                db, user_id, name
            )
            
            if not collection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Collection '{name}' not found"
                )
            
            logger.info(f"Searching collection '{name}' with query: {query[:50]}...")
            
            # Search using VectorService
            vector_service = get_vector_service()
            full_name = f"{user_id}_{name}"
            
            result = await vector_service.search(
                collection_name=full_name,
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                metadata_filter=metadata_filter
            )
            
            logger.info(f"Search completed. Found {result['total_results']} results")
            
            return {
                "query": query,
                "collection_name": name,
                "results": result["results"],
                "total_results": result["total_results"],
                "top_k": top_k,
                "score_threshold": score_threshold
            }
            
        except HTTPException:
            raise
        except FileNotFoundError:
            logger.error(f"FAISS index not found for collection '{name}'")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection index not found. It may have been deleted."
            )
        except Exception as e:
            logger.error(f"Search failed in collection '{name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Search failed: {str(e)}"
            )
    
    @staticmethod
    async def delete_collection(
        db: AsyncSession,
        user_id: UUID,
        name: str
    ) -> None:
        """
        Delete a collection.
        
        Args:
            db: Database session
            user_id: User ID
            name: Collection name
        
        Raises:
            HTTPException: If collection not found or deletion fails
        """
        try:
            # Get collection
            collection = await VectorCollectionService.get_collection_by_name(
                db, user_id, name
            )
            
            if not collection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Collection '{name}' not found"
                )
            
            logger.info(f"Deleting collection '{name}'")
            
            # Delete FAISS index
            vector_service = get_vector_service()
            full_name = f"{user_id}_{name}"
            
            await vector_service.delete_collection(full_name)
            
            # Delete database record
            await db.delete(collection)
            await db.commit()
            
            logger.info(f"Collection '{name}' deleted successfully")
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete collection '{name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete collection: {str(e)}"
            )


