"""Vector collection routes"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.schemas.vector import (
    VectorCollectionCreate,
    VectorCollectionResponse,
    VectorCollectionListItem,
    VectorDocumentAdd,
    VectorDocumentAddResponse,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorSearchResult
)
from app.models.user import User
from app.services.vector_collection_service import VectorCollectionService
from app.services.file_parser_service import FileParserService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/collections", response_model=List[VectorCollectionListItem])
async def list_collections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all vector collections for the current user.
    
    Returns a list of collections with basic metadata including:
    - Collection ID
    - Name
    - Document count
    - Dimension
    - Creation date
    """
    logger.info(f"Listing collections for user {current_user.id}")
    
    collections = await VectorCollectionService.list_collections(
        db=db,
        user_id=current_user.id
    )
    
    return collections


@router.post("/collections", response_model=VectorCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: VectorCollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new vector collection with initial documents.
    
    The collection will be created with:
    - A unique name (scoped to the user)
    - Initial set of documents with embeddings
    - FAISS index for similarity search
    
    Example request:
    ```json
    {
      "name": "tech_knowledge",
      "documents": [
        {
          "text": "Python is a programming language",
          "metadata": {"category": "programming"}
        },
        {
          "text": "FastAPI is a web framework",
          "metadata": {"category": "web"}
        }
      ]
    }
    ```
    """
    logger.info(f"Creating collection '{collection_data.name}' for user {current_user.id}")
    
    # Convert documents to format expected by service
    documents = [
        {
            "text": doc.text,
            "metadata": doc.metadata or {}
        }
        for doc in collection_data.documents
    ]
    
    collection = await VectorCollectionService.create_collection(
        db=db,
        user_id=current_user.id,
        name=collection_data.name,
        documents=documents
    )
    
    return collection


@router.post(
    "/collections/{collection_name}/documents",
    response_model=VectorDocumentAddResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_documents(
    collection_name: str,
    document_data: VectorDocumentAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add documents to an existing collection.
    
    Documents will be:
    - Embedded using the same model as the collection
    - Added to the FAISS index
    - Searchable immediately after addition
    
    Example request:
    ```json
    {
      "documents": [
        {
          "text": "LangChain is a framework for LLM applications",
          "metadata": {"category": "ai"}
        },
        {
          "text": "PostgreSQL is a relational database",
          "metadata": {"category": "database"}
        }
      ]
    }
    ```
    """
    logger.info(f"Adding documents to collection '{collection_name}'")
    
    # Validate documents
    if not document_data.documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents provided"
        )
    
    # Convert documents to format expected by service
    documents = [
        {
            "text": doc.text,
            "metadata": doc.metadata or {}
        }
        for doc in document_data.documents
    ]
    
    result = await VectorCollectionService.add_documents(
        db=db,
        user_id=current_user.id,
        name=collection_name,
        documents=documents
    )
    
    return result


@router.post(
    "/collections/{collection_name}/upload",
    response_model=VectorDocumentAddResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_files(
    collection_name: str,
    files: List[UploadFile] = File(...),
    metadata_json: Optional[str] = Form(None),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse files to add documents to a collection.
    
    Supported file types:
    - PDF (.pdf)
    - Microsoft Word (.docx, .doc)
    - Plain Text (.txt, .md)
    
    Files will be:
    - Parsed to extract text content
    - Chunked into smaller pieces (for large documents)
    - Embedded and added to the FAISS index
    - Searchable immediately after upload
    
    Parameters:
    - files: One or more files to upload (multipart/form-data)
    - metadata_json: Optional JSON string with metadata to apply to all documents
    - chunk_size: Size of text chunks in characters (default: 1000)
    - chunk_overlap: Overlap between chunks in characters (default: 200)
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/vectors/collections/my_collection/upload" \
      -H "Authorization: Bearer TOKEN" \
      -F "files=@document.pdf" \
      -F "files=@another.docx" \
      -F "metadata_json={\"source\": \"uploaded\", \"category\": \"docs\"}"
    ```
    """
    logger.info(f"Uploading {len(files)} file(s) to collection '{collection_name}'")
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Parse optional metadata
    shared_metadata = {}
    if metadata_json:
        try:
            import json
            shared_metadata = json.loads(metadata_json)
            if not isinstance(shared_metadata, dict):
                raise ValueError("metadata_json must be a JSON object")
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metadata_json format: {str(e)}"
            )
    
    # Parse all files and extract documents
    all_documents = []
    file_errors = []
    
    for file in files:
        try:
            # Read file content
            content = await file.read()
            
            if not content:
                file_errors.append(f"{file.filename}: File is empty")
                continue
            
            # Parse file and extract text chunks
            file_documents = await FileParserService.parse_file(
                filename=file.filename or "unknown",
                content=content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # Merge shared metadata with file-specific metadata
            for doc in file_documents:
                doc["metadata"] = {**shared_metadata, **doc.get("metadata", {})}
            
            all_documents.extend(file_documents)
            
            logger.info(f"Successfully parsed {file.filename}: {len(file_documents)} chunks")
            
        except Exception as e:
            error_msg = f"{file.filename}: {str(e)}"
            file_errors.append(error_msg)
            logger.error(f"Failed to parse file {file.filename}: {str(e)}")
            # Continue processing other files
    
    if not all_documents:
        error_detail = "No documents extracted from files. "
        if file_errors:
            error_detail += "Errors: " + "; ".join(file_errors)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    
    # Check if collection exists, create if it doesn't
    existing_collection = await VectorCollectionService.get_collection_by_name(
        db=db,
        user_id=current_user.id,
        name=collection_name
    )
    
    if not existing_collection:
        logger.info(f"Collection '{collection_name}' does not exist, creating it with uploaded files")
        # Create collection with the parsed documents
        collection = await VectorCollectionService.create_collection(
            db=db,
            user_id=current_user.id,
            name=collection_name,
            documents=all_documents
        )
        
        response_data = {
            "collection_name": collection_name,
            "documents_added": len(all_documents),
            "total_documents": collection.document_count,
            "status": "success",
            "files_processed": len(files) - len(file_errors),
            "files_failed": len(file_errors),
            "errors": file_errors if file_errors else None
        }
        
        return response_data
    
    # Add documents to existing collection
    try:
        result = await VectorCollectionService.add_documents(
            db=db,
            user_id=current_user.id,
            name=collection_name,
            documents=all_documents
        )
        
        # Include file parsing info in response
        response_data = {
            "collection_name": result["collection_name"],
            "documents_added": len(all_documents),
            "total_documents": result["total_documents"],
            "status": "success",
            "files_processed": len(files) - len(file_errors),
            "files_failed": len(file_errors),
            "errors": file_errors if file_errors else None
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to add documents to collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add documents to collection: {str(e)}"
        )


@router.post("/collections/{collection_name}/search", response_model=VectorSearchResponse)
async def search_collection(
    collection_name: str,
    search_request: VectorSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search in a vector collection using semantic similarity.
    
    The search will:
    - Convert query to embeddings
    - Find most similar documents in FAISS index
    - Return ranked results with similarity scores
    - Apply optional filters
    
    Example request:
    ```json
    {
      "query": "What is FastAPI?",
      "top_k": 5,
      "score_threshold": 0.3,
      "metadata_filter": {
        "category": "web"
      }
    }
    ```
    
    Example response:
    ```json
    {
      "query": "What is FastAPI?",
      "collection_name": "tech_knowledge",
      "results": [
        {
          "text": "FastAPI is a web framework",
          "score": 0.92,
          "metadata": {"category": "web"}
        }
      ],
      "total_results": 1,
      "top_k": 5,
      "score_threshold": 0.3
    }
    ```
    """
    logger.info(f"Searching collection '{collection_name}' with query: {search_request.query[:50]}...")
    
    result = await VectorCollectionService.search_collection(
        db=db,
        user_id=current_user.id,
        name=collection_name,
        query=search_request.query,
        top_k=search_request.top_k,
        score_threshold=search_request.score_threshold,
        metadata_filter=search_request.metadata_filter
    )
    
    return result


@router.delete("/collections/{collection_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a vector collection.
    
    This will:
    - Remove the FAISS index from disk
    - Delete the collection metadata from database
    - Cannot be undone
    
    Returns 204 No Content on success.
    """
    logger.info(f"Deleting collection '{collection_name}' for user {current_user.id}")
    
    await VectorCollectionService.delete_collection(
        db=db,
        user_id=current_user.id,
        name=collection_name
    )
    
    return None


@router.get("/collections/{collection_name}", response_model=VectorCollectionResponse)
async def get_collection(
    collection_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific collection.
    
    Returns:
    - Collection metadata
    - Document count
    - Dimension of embeddings
    - Creation date
    """
    logger.info(f"Getting collection '{collection_name}' for user {current_user.id}")
    
    collection = await VectorCollectionService.get_collection_by_name(
        db=db,
        user_id=current_user.id,
        name=collection_name
    )
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{collection_name}' not found"
        )
    
    return collection
