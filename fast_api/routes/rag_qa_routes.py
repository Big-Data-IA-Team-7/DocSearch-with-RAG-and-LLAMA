from fastapi import APIRouter
from typing import Optional
from fast_api.schemas.request_schemas import MultiModalRagRequest
from fast_api.services.data_service import download_file
from fast_api.services.rag_service import create_vector_index, query_vector_index
from fast_api.services.multi_modal.document_parser import load_multimodal_data
from fast_api.config.config_settings import initialize_settings, initialize_summary_settings

router = APIRouter()

@router.get("/fetch-rag-response/", response_model=Optional[str])
def get_mmr_response(user_question: str, generate_summary: Optional[bool] = None):
    
    if generate_summary:
        initialize_summary_settings()
    else:
        initialize_settings()

    index_name = 'vectorindex'

    response = query_vector_index(index_name, user_question)

    return response