from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    status: str
    added_chunks: int
    document_id: str
    document_name: str
    document_type: str


class DocumentDeleteRequest(BaseModel):
    document_id: Optional[str] = None


class DocumentSummary(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    upload_date: str
    chunk_count: int
    user_id: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentSummary]


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    session_id: Optional[str] = None
    use_hybrid_search: Optional[bool] = True
    use_reranking: Optional[bool] = True


class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    session_id: str