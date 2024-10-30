# routers/index.py
from fastapi import APIRouter, Depends, HTTPException
from fast_api.schemas.request_schemas import FileIndexRequest
from fast_api.config.config_settings import get_pinecone_client, initialize_settings
from fast_api.services.multi_modal.document_parser import load_multimodal_data
from fast_api.services.rag_service import create_vector_index

router = APIRouter()

@router.post("/create_index")
def create_index(request: FileIndexRequest, pinecone_client = Depends(get_pinecone_client)):
    try:
        file_name = request.file_name
        pdf_content = request.pdf_content

        pincecone_indexes = pinecone_client.list_indexes()
        # Check if index exists in Pinecone
        if any(index["name"] == file_name for index in pincecone_indexes["indexes"]):
            
            status = "index_already_exists"
            
        else:
            
            initialize_settings()

            # Create Document and new VectorIndex, then add to Pinecone
            file_detail = {"name": file_name, "content": pdf_content}
            documents = load_multimodal_data(file_detail)

            vector_index = create_vector_index(pinecone_client, file_name, documents)
            status = "index_created"
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))