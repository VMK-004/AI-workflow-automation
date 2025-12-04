# Vector Collections API - Complete Guide

## Overview

The Vector Collections API provides complete CRUD operations for managing FAISS vector collections. Each collection stores documents with their embeddings and supports semantic similarity search.

## Architecture

### Components

1. **VectorCollectionService** (`app/services/vector_collection_service.py`)
   - Manages collection metadata in PostgreSQL
   - Coordinates with VectorService for FAISS operations
   - Handles user authorization

2. **VectorService** (`app/services/vector_service.py`)
   - Manages FAISS indices on disk
   - Handles embeddings generation
   - Performs similarity searches

3. **VectorCollection Model** (`app/models/vector_collection.py`)
   - PostgreSQL table for collection metadata
   - Tracks document count, dimension, index path

4. **API Routes** (`app/api/routes/vectors.py`)
   - RESTful endpoints
   - Request validation with Pydantic
   - User authentication required

## Features

✅ **Create Collections** - Initialize with documents  
✅ **List Collections** - View all user collections  
✅ **Add Documents** - Expand existing collections  
✅ **Semantic Search** - Find similar documents  
✅ **Delete Collections** - Remove indices and metadata  
✅ **User Isolation** - Collections scoped per user  
✅ **Metadata Filtering** - Filter search results  
✅ **Score Thresholding** - Control result quality  

## API Endpoints

### 1. Create Collection

**POST** `/api/vectors/collections`

Create a new vector collection with initial documents.

**Request Body:**
```json
{
  "name": "tech_knowledge",
  "documents": [
    {
      "text": "Python is a high-level programming language",
      "metadata": {
        "category": "programming",
        "language": "python"
      }
    },
    {
      "text": "FastAPI is a modern web framework for Python",
      "metadata": {
        "category": "web",
        "framework": "fastapi"
      }
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "abc-123-def-456",
  "user_id": "user-uuid",
  "name": "tech_knowledge",
  "dimension": 384,
  "document_count": 2,
  "created_at": "2025-11-24T10:30:00Z",
  "index_path": "data/faiss/user-uuid_tech_knowledge"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Validation:**
- Name must be alphanumeric with underscores/hyphens
- At least 1 document required
- Text cannot be empty
- Metadata is optional

**Errors:**
- `400` - Collection already exists or invalid input
- `500` - Failed to create FAISS index

---

### 2. List Collections

**GET** `/api/vectors/collections`

List all vector collections for the current user.

**Response (200 OK):**
```json
[
  {
    "id": "abc-123-def-456",
    "name": "tech_knowledge",
    "document_count": 5,
    "dimension": 384,
    "created_at": "2025-11-24T10:30:00Z"
  },
  {
    "id": "xyz-789-uvw-012",
    "name": "company_docs",
    "document_count": 120,
    "dimension": 384,
    "created_at": "2025-11-23T15:20:00Z"
  }
]
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3. Get Collection Details

**GET** `/api/vectors/collections/{collection_name}`

Get detailed information about a specific collection.

**Response (200 OK):**
```json
{
  "id": "abc-123-def-456",
  "user_id": "user-uuid",
  "name": "tech_knowledge",
  "dimension": 384,
  "document_count": 5,
  "created_at": "2025-11-24T10:30:00Z",
  "index_path": "data/faiss/user-uuid_tech_knowledge"
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/vectors/collections/tech_knowledge \
  -H "Authorization: Bearer $TOKEN"
```

**Errors:**
- `404` - Collection not found

---

### 4. Add Documents

**POST** `/api/vectors/collections/{collection_name}/documents`

Add documents to an existing collection.

**Request Body:**
```json
{
  "documents": [
    {
      "text": "LangChain is a framework for LLM applications",
      "metadata": {
        "category": "ai",
        "tool": "langchain"
      }
    },
    {
      "text": "PostgreSQL is a relational database",
      "metadata": {
        "category": "database",
        "type": "sql"
      }
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "collection_name": "tech_knowledge",
  "documents_added": 2,
  "total_documents": 7,
  "status": "success"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/vectors/collections/tech_knowledge/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "text": "FAISS is a library for similarity search",
        "metadata": {"category": "search"}
      }
    ]
  }'
```

**Validation:**
- At least 1 document required
- Text cannot be empty
- Collection must exist

**Errors:**
- `404` - Collection not found
- `400` - No documents provided
- `500` - Failed to add documents

---

### 5. Search Collection

**POST** `/api/vectors/collections/{collection_name}/search`

Perform semantic similarity search in a collection.

**Request Body:**
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

**Parameters:**
- `query` (required): Search query text
- `top_k` (optional, default: 5): Number of results (max 100)
- `score_threshold` (optional): Minimum similarity score (0.0-1.0)
- `metadata_filter` (optional): Filter by metadata key-value pairs

**Response (200 OK):**
```json
{
  "query": "What is FastAPI?",
  "collection_name": "tech_knowledge",
  "results": [
    {
      "text": "FastAPI is a modern web framework for Python",
      "score": 0.92,
      "metadata": {
        "category": "web",
        "framework": "fastapi"
      }
    },
    {
      "text": "Python is a high-level programming language",
      "score": 0.65,
      "metadata": {
        "category": "programming",
        "language": "python"
      }
    }
  ],
  "total_results": 2,
  "top_k": 5,
  "score_threshold": 0.3
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/vectors/collections/tech_knowledge/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 3,
    "score_threshold": 0.5
  }'
```

**Errors:**
- `404` - Collection not found
- `400` - Invalid parameters
- `500` - Search failed

---

### 6. Delete Collection

**DELETE** `/api/vectors/collections/{collection_name}`

Delete a vector collection permanently.

**Response (204 No Content)**

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/vectors/collections/tech_knowledge \
  -H "Authorization: Bearer $TOKEN"
```

**Effects:**
- Removes FAISS index from disk
- Deletes metadata from database
- Cannot be undone

**Errors:**
- `404` - Collection not found
- `500` - Failed to delete

---

## Complete Testing Workflow

### Step 1: Authentication

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "vectoruser",
    "email": "vector@example.com",
    "password": "vector123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "vectoruser",
    "password": "vector123"
  }'

# Save token
export TOKEN="<your_access_token>"
```

### Step 2: Create Collection

```bash
curl -X POST http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ai_knowledge",
    "documents": [
      {
        "text": "Machine learning is a subset of artificial intelligence",
        "metadata": {"topic": "ml", "level": "intro"}
      },
      {
        "text": "Neural networks are computing systems inspired by biological brains",
        "metadata": {"topic": "nn", "level": "intermediate"}
      },
      {
        "text": "Deep learning uses multiple layers to extract features",
        "metadata": {"topic": "dl", "level": "advanced"}
      }
    ]
  }'
```

### Step 3: List Collections

```bash
curl -X GET http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN"
```

### Step 4: Add More Documents

```bash
curl -X POST http://localhost:8000/api/vectors/collections/ai_knowledge/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "text": "Natural language processing enables computers to understand human language",
        "metadata": {"topic": "nlp", "level": "intermediate"}
      },
      {
        "text": "Computer vision allows machines to interpret visual information",
        "metadata": {"topic": "cv", "level": "intermediate"}
      }
    ]
  }'
```

### Step 5: Search Collection

```bash
# Basic search
curl -X POST http://localhost:8000/api/vectors/collections/ai_knowledge/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is deep learning?",
    "top_k": 3
  }'

# Search with threshold
curl -X POST http://localhost:8000/api/vectors/collections/ai_knowledge/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "neural networks and AI",
    "top_k": 5,
    "score_threshold": 0.5
  }'

# Search with metadata filter
curl -X POST http://localhost:8000/api/vectors/collections/ai_knowledge/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "top_k": 5,
    "metadata_filter": {
      "level": "intermediate"
    }
  }'
```

### Step 6: Get Collection Details

```bash
curl -X GET http://localhost:8000/api/vectors/collections/ai_knowledge \
  -H "Authorization: Bearer $TOKEN"
```

### Step 7: Delete Collection

```bash
curl -X DELETE http://localhost:8000/api/vectors/collections/ai_knowledge \
  -H "Authorization: Bearer $TOKEN"
```

---

## Integration with Workflows

You can now use vector collections in your workflows with the `faiss_search` node:

```bash
# Create workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RAG Pipeline",
    "description": "Retrieval-Augmented Generation"
  }'

WORKFLOW_ID="<save_id>"

# Create FAISS search node
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/nodes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_knowledge",
    "node_type": "faiss_search",
    "config": {
      "collection_name": "ai_knowledge",
      "query": "{user_question}",
      "top_k": 3
    }
  }'

# Execute workflow
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "user_question": "What is deep learning?"
    }
  }'
```

---

## Database Schema

### vector_collections Table

```sql
CREATE TABLE vector_collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    dimension INTEGER NOT NULL,
    index_path VARCHAR(512),
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_user_collection_name UNIQUE(user_id, name)
);

CREATE INDEX idx_vector_collections_user_id ON vector_collections(user_id);
```

---

## File Storage

FAISS indices are stored in: `data/faiss/{user_id}_{collection_name}/`

Each index directory contains:
- `index.faiss` - FAISS index file
- `index.pkl` - Metadata pickle file

---

## Performance Considerations

### Embeddings Model
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimension**: 384
- **Speed**: ~1000 documents/second
- **Size**: ~90MB

### Search Performance
- **<10K documents**: <100ms
- **10K-100K documents**: 100-500ms
- **>100K documents**: Consider IndexIVFFlat

### Scaling Recommendations
1. **Up to 100K docs**: Use default FAISS IndexFlatL2
2. **100K-1M docs**: Use IndexIVFFlat with clustering
3. **>1M docs**: Use faiss-gpu + sharding

---

## Error Handling

All endpoints return appropriate HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | Success (GET, POST search) |
| 201 | Created (POST create, add docs) |
| 204 | No Content (DELETE) |
| 400 | Bad Request (validation error) |
| 404 | Not Found (collection doesn't exist) |
| 500 | Internal Server Error (operation failed) |

---

## Best Practices

### 1. Collection Naming
- Use descriptive names: `product_docs`, `user_feedback`
- Avoid special characters
- Keep names short and lowercase

### 2. Document Structure
- Keep text focused and coherent
- Add meaningful metadata for filtering
- Chunk large documents into smaller pieces

### 3. Metadata Design
```json
{
  "category": "technical",
  "source": "documentation",
  "date": "2025-11-24",
  "author": "john_doe",
  "version": "1.0"
}
```

### 4. Search Optimization
- Use `score_threshold` to filter low-quality results
- Start with `top_k=5`, adjust based on needs
- Use metadata filters to narrow results

### 5. Batch Operations
- Add documents in batches of 100-1000
- Avoid creating many small collections
- Consolidate related documents

---

## Use Cases

### 1. RAG (Retrieval-Augmented Generation)
```
User Query → FAISS Search → LLM with Context → Response
```

### 2. Semantic Search
```
Search Query → FAISS → Ranked Results → Display
```

### 3. Document Clustering
```
Documents → Embeddings → FAISS → Similar Docs → Clusters
```

### 4. Duplicate Detection
```
New Doc → FAISS Search → Check Similarity → Flag Duplicates
```

---

## Next Steps

1. **Test the API**: Follow the complete testing workflow above
2. **Build RAG Pipeline**: Combine with LLM nodes
3. **Add Frontend**: UI for collection management
4. **Monitor Performance**: Track search latency
5. **Scale**: Implement sharding for large datasets

---

## Status

✅ **Complete** - All endpoints implemented and tested  
✅ **Production Ready** - Error handling, validation, logging  
✅ **User Isolated** - Collections scoped per user  
✅ **Fully Integrated** - Works with workflows and node handlers  

---

**Ready to use!** Start building semantic search and RAG applications! 🚀


