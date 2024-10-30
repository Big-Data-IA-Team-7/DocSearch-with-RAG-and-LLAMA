from fastapi import APIRouter, HTTPException, Depends
from fast_api.schemas.request_schemas import MultiModalRagRequest
from fast_api.config.config_settings import get_pinecone_client
from fast_api.services.rag_service import query_vector_index

router = APIRouter()

@router.post("/ask_question/{file_name}")
def ask_question(request: MultiModalRagRequest, pinecone_client = Depends(get_pinecone_client)):
    try:
        # Initialize the query engine and get the answer
        file_name = request.file_name
        user_question = request.user_question
        response = query_vector_index(file_name, user_question, pinecone_client)
        return response
        # return {"answer": answer, "chat_history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))