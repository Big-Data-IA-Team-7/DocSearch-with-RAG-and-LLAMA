from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fast_api.config.config_settings import get_pinecone_client
from fast_api.services.rag_service import retrieve_query, create_generate_summary, create_summary_index, retrieve_summary_response
from fast_api.services.report_service import report_generate
from fast_api.services.data_service import download_file
from fast_api.config.config_settings import initialize_settings, initialize_summary_settings
from fast_api.services.multi_modal.document_parser import load_multimodal_data
from fastapi.responses import JSONResponse
import re
import logging

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

@router.get("/ask-question/")
def ask_question(file_name: str, user_question: str, pinecone_client = Depends(get_pinecone_client)):
    try:

        file_name = file_name.replace(".pdf", "")

        # Initialize the query engine and get the answer
        initialize_settings()
        response = retrieve_query(file_name, user_question, pinecone_client)
        logging.debug(f"Response received: {response}")
        return response
        # return {"answer": answer, "chat_history": chat_history}
    except Exception as e:
        logging.error("Error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/generate-summary/")
def generate_summary(file_name: str = Form(...),
    pdf_content: UploadFile = File(...)):
    try:
        # Initialize the query engine and get the answer
        initialize_summary_settings()

        file_detail = {"name": file_name, "content": pdf_content.file}
        documents = load_multimodal_data(file_detail)

        response = create_generate_summary(documents)

        logging.debug(f"Response received: {response}")
        return response
        # return {"answer": answer, "chat_history": chat_history}
    except Exception as e:
        logging.error("Error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/retrieve-summary/")
def retrieve_summary(file_name: str = Form(...),
    pdf_content: UploadFile = File(...),
    pinecone_client = Depends(get_pinecone_client)):
    try:
        # Initialize the query engine and get the answer
        match = re.match(r"(\d+)_(.*)\.pdf$", file_name)
        if match:
            number = match.group(1)
            rest_of_name = match.group(2)
            worded_number = number_to_word.get(number, number)  # Get worded number if exists
            file_name = f"{worded_number}{rest_of_name}summary"
        
        initialize_summary_settings()
        
        if pinecone_client.has_index(file_name):
            
            status = "index_already_exists"
            
            response = retrieve_summary_response(pinecone_client, file_name)
            
        else:

            # Create Document and new VectorIndex, then add to Pinecone
            file_detail = {"name": file_name, "content": pdf_content.file}
            documents = load_multimodal_data(file_detail)

            vector_index = create_summary_index(pinecone_client, file_name, documents)

            logging.info("Summary Index created.")

            response = retrieve_summary_response(pinecone_client, file_name)

        response = create_generate_summary(pinecone_client, file_name)

        logging.debug(f"Response received: {response}")
        return response
        # return {"answer": answer, "chat_history": chat_history}
    except Exception as e:
        logging.error("Error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/generate-report/")
def generate_report(file_name: str, file_path: str, user_input: str):
    try:
        file_object = download_file(file_name)
        file_name = file_name.replace(".pdf", "")
        file_path = file_object["file_path"]
    
        response = report_generate(file_path, user_input, file_name)

        return JSONResponse(content=response.dict())
    except Exception as e:
        logging.error("Error", e)
        raise HTTPException(status_code=500, detail=str(e))