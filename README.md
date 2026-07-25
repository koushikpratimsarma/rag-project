# RAG Document QA
A simple Retrieval-Augmented Generation (RAG) project for document question-answering. Upload documents, build embeddings, and ask questions over your documents.

## What it does

- Upload PDFs or text files.
- Split documents into chunks and create embeddings.
- Store embeddings in a vector database (Qdrant).
- Query documents with semantic search and get answers.
- Simple Streamlit UI and FastAPI backend.

## Quick start

Requirements: Python 3.10+, pip. Docker optional.

1. Create & activate venv (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with minimal vars (example):

```env
EMBEDDING_PROVIDER=sentence_transformers
SECRET_KEY=change_this_for_project
QDRANT_URL=http://localhost:6333
```

4. Run backend:

```bash
uvicorn backend.main:app --reload
```

5. Run frontend (in new terminal):

```bash
streamlit run frontend/app.py
```

Open: Frontend `http://localhost:8501`, API docs `http://localhost:8000/docs`

## Important files

- `backend/` - FastAPI API, auth, data files
- `backend/rag/` - chunking, embeddings, search logic
- `frontend/` - Streamlit UI
- `requirements.txt` - Python packages
- `docker-compose.yml` and `DOCKER_GUIDE.md` - optional Docker setup

## How to test (quick)

1. Register a user:

```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"username":"you","password":"pass"}'
```

2. Login to get token:

```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"username":"you","password":"pass"}'
```

3. Upload a PDF (use the token):

```bash
curl -X POST http://localhost:8000/upload -H "Authorization: Bearer TOKEN" -F "file=@/path/to/doc.pdf"
```

4. Ask a question:

```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d '{"query":"What is this doc about?"}'
```

## Document upload & ingestion

Endpoints allow single or batch uploads. Uploaded documents are extracted, chunked, embedded and persisted to the vector store.

Single upload example:

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf"
```

Batch upload example:

```bash
curl -X POST http://localhost:8000/upload_batch \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@/path/file1.pdf" \
  -F "files=@/path/file2.txt"
```

## Querying

Basic query:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"What is the main topic?"}'
```

Advanced query with options (hybrid search, reranking, metadata filters):

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query":"What is the main topic?",
    "top_k":5,
    "use_hybrid_search":true,
    "use_reranking":true,
    "metadata_filters":{"document_type":"pdf"}
  }'
```

## 📜 Query History & Sessions

### Get Query History
```bash
curl http://localhost:8000/history/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Conversation Sessions
```bash
curl http://localhost:8000/history/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Specific Session
```bash
curl http://localhost:8000/history/session/{session_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search History
```bash
curl "http://localhost:8000/history/search?q=keyword" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Config (minimum)

- `EMBEDDING_PROVIDER` — `sentence_transformers` (local) or `openai` (requires API key)
- `QDRANT_URL` — `http://localhost:6333` (use Docker or external Qdrant)
- `SECRET_KEY` — set a value for JWT

Look at `backend/config.py` for more options.

## Tips

- Use small sample PDFs to test first.
- Use local models (`sentence_transformers`) to avoid paying for API calls.
- Focus your report on: problem, architecture (backend + frontend), experiments (queries & results), and limitations.
Files to check when writing your report: `backend/main.py`, `frontend/app.py`, and `backend/rag/` code.

