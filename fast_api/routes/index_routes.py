# routers/index.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fast_api.config.config_settings import get_pinecone_client, initialize_settings
from fast_api.services.multi_modal.document_parser import load_multimodal_data
from fast_api.services.rag_service import create_vector_index
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

@router.post("/create-index/")
def create_index(file_name: str = Form(...),
    pdf_content: UploadFile = File(...),
    pinecone_client=Depends(get_pinecone_client)):
    try:

        file_name = file_name.replace(".pdf", "")
        # Check if index exists in Pinecone
        if pinecone_client.has_index(file_name):
            
            status = "index_already_exists"
            
        else:
            
            initialize_settings()

            # Create Document and new VectorIndex, then add to Pinecone
            file_detail = {"name": file_name, "content": pdf_content.file}
            documents = load_multimodal_data(file_detail)

            vector_index = create_vector_index(pinecone_client, file_name, documents)
            status = "index_created"
        return {"status": status}
    except Exception as e:
            logging.error(f"Error in index creation process: {e}")
            raise HTTPException(status_code=500, detail="Error creating index")
        