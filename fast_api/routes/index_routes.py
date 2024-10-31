# routers/index.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fast_api.config.config_settings import get_pinecone_client, initialize_settings
from fast_api.services.multi_modal.document_parser import load_multimodal_data
from fast_api.services.rag_service import create_vector_index
import logging
import re

# Dictionary to map numbers to words
number_to_word = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine"
}

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

@router.post("/create-index/")
def create_index(file_name: str = Form(...),
    pdf_content: UploadFile = File(...),
    pinecone_client=Depends(get_pinecone_client)):
    try:
        match = re.match(r"(\d+)_(.*)\.pdf$", file_name)
        if match:
            number = match.group(1)
            rest_of_name = match.group(2)
            worded_number = number_to_word.get(number, number)  # Get worded number if exists
            file_name = f"{worded_number}{rest_of_name}"
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
        