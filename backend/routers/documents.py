from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form
from backend.history import add_history

from backend.auth import get_current_user_optional
from backend.schemas.documents import (
    DocumentDeleteRequest,
    DocumentListResponse,
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
)
from backend.services.document_service import (
    delete_document_by_id,
    list_uploaded_documents,
    process_document_upload,
    query_uploaded_documents,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Optional[str] = Depends(get_current_user_optional),
) -> DocumentUploadResponse:
    return await process_document_upload(file, current_user)


@router.post("/upload_batch")
async def upload_documents_batch(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    current_user: Optional[str] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    results = []
    errors = []

    for file in files:
        try:
            result = await process_document_upload(
                file=file,
                current_user=current_user,
                session_id=session_id,
            )
            results.append(result.model_dump())
        except Exception as exc:
            errors.append({"filename": file.filename, "error": str(exc)})

    return {
        "status": "completed",
        "successful_uploads": len(results),
        "failed_uploads": len(errors),
        "results": results,
        "errors": errors,
    }


@router.get("/list", response_model=DocumentListResponse)
def list_documents(
    session_id: Optional[str] = None,
    current_user: Optional[str] = Depends(get_current_user_optional),
) -> DocumentListResponse:
    return list_uploaded_documents(current_user, session_id)


@router.delete("/delete")
def delete_document(
    request: DocumentDeleteRequest,
    current_user: Optional[str] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    return delete_document_by_id(request.document_id, current_user)


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: Optional[str] = Depends(get_current_user_optional),
) -> QueryResponse:
    result = await query_uploaded_documents(request, current_user)

    if current_user:
        session_id = request.session_id or result.session_id

        add_history(
            username=current_user,
            query=request.query,
            answer=result.answer,
            retrieved_chunks=[
                citation.model_dump() if hasattr(citation, "model_dump") else citation
                for citation in getattr(result, "citations", [])
            ],
            documents_used=[
                citation.document_name
                for citation in getattr(result, "citations", [])
                if hasattr(citation, "document_name")
            ],
            session_id=session_id,
        )

    return result