"""Vector collection schemas"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional


class DocumentInput(BaseModel):
    """Schema for a single document input"""
    text: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class VectorCollectionCreate(BaseModel):
    """Schema for creating a vector collection"""
    name: str = Field(..., min_length=1, max_length=255, description="Collection name")
    documents: List[DocumentInput] = Field(..., min_items=1, description="Initial documents")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate collection name"""
        # Allow alphanumeric, underscores, hyphens
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Collection name must contain only letters, numbers, underscores, and hyphens')
        return v


class VectorCollectionResponse(BaseModel):
    """Schema for vector collection response"""
    id: UUID
    user_id: UUID
    name: str
    dimension: int
    document_count: int
    created_at: datetime
    index_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class VectorCollectionListItem(BaseModel):
    """Schema for collection list item"""
    id: UUID
    name: str
    document_count: int
    dimension: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class VectorDocumentAdd(BaseModel):
    """Schema for adding documents to collection"""
    documents: List[DocumentInput] = Field(..., min_items=1, description="Documents to add")


class VectorDocumentAddResponse(BaseModel):
    """Schema for add documents response"""
    collection_name: str
    documents_added: int
    total_documents: int
    status: str = "success"
    files_processed: Optional[int] = None
    files_failed: Optional[int] = None
    errors: Optional[List[str]] = None


class VectorSearchRequest(BaseModel):
    """Schema for vector search request"""
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=5, gt=0, le=100, description="Number of results to return")
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum similarity score")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Filter by metadata")


class VectorSearchResult(BaseModel):
    """Schema for single search result"""
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorSearchResponse(BaseModel):
    """Schema for vector search response"""
    query: str
    collection_name: str
    results: List[VectorSearchResult]
    total_results: int
    top_k: int
    score_threshold: Optional[float] = None
