# Vector Collections API - Quick Test

## Setup (30 seconds)

```bash
# Start server
cd backend
uvicorn app.main:app --reload

# Get token (if not already logged in)
export TOKEN="your_jwt_token"
```

## Test 1: Create Collection (1 minute)

```bash
curl -X POST http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "quicktest",
    "documents": [
      {"text": "Python is a programming language", "metadata": {"type": "lang"}},
      {"text": "FastAPI is a web framework", "metadata": {"type": "framework"}},
      {"text": "PostgreSQL is a database", "metadata": {"type": "db"}}
    ]
  }'
```

**Expected**: 201 Created with collection details

## Test 2: List Collections (10 seconds)

```bash
curl -X GET http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: Array with "quicktest" collection

## Test 3: Add Documents (30 seconds)

```bash
curl -X POST http://localhost:8000/api/vectors/collections/quicktest/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"text": "FAISS is for vector search", "metadata": {"type": "library"}},
      {"text": "LangChain is for LLM apps", "metadata": {"type": "framework"}}
    ]
  }'
```

**Expected**: 201 Created, total_documents: 5

## Test 4: Search (30 seconds)

```bash
curl -X POST http://localhost:8000/api/vectors/collections/quicktest/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is FastAPI?",
    "top_k": 3
  }'
```

**Expected**: Results with "FastAPI" as top match

## Test 5: Search with Filter (30 seconds)

```bash
curl -X POST http://localhost:8000/api/vectors/collections/quicktest/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "programming",
    "top_k": 3,
    "metadata_filter": {"type": "framework"}
  }'
```

**Expected**: Only framework results (FastAPI, LangChain)

## Test 6: Get Collection (10 seconds)

```bash
curl -X GET http://localhost:8000/api/vectors/collections/quicktest \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: Collection details with document_count: 5

## Test 7: Delete Collection (10 seconds)

```bash
curl -X DELETE http://localhost:8000/api/vectors/collections/quicktest \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: 204 No Content

## Verify Deletion (10 seconds)

```bash
curl -X GET http://localhost:8000/api/vectors/collections \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: Empty array or no "quicktest"

---

## All Tests Pass? ✅

You now have a fully functional vector collections API!

## Common Issues

### "Embeddings model not loaded"
Wait 2-3 seconds for model to load on first use.

### "Collection already exists"
Use a different name or delete the existing one.

### "Collection not found"
Check spelling and ensure you're using the correct token.

---

**Total Time**: ~3 minutes  
**Status**: 🟢 Ready to use!





