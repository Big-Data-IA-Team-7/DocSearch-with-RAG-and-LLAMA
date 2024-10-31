from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fast_api.config.config_settings import get_pinecone_client
from fast_api.services.rag_service import retrieve_query, generate_summary
from fast_api.config.config_settings import initialize_settings, initialize_summary_settings
from fast_api.services.multi_modal.document_parser import load_multimodal_data
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

        match = re.match(r"(\d+)_(.*)\.pdf$", file_name)
        if match:
            number = match.group(1)
            rest_of_name = match.group(2)
            worded_number = number_to_word.get(number, number)  # Get worded number if exists
            file_name = f"{worded_number}{rest_of_name}"
        

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
def ask_question(file_name: str = Form(...),
    pdf_content: UploadFile = File(...)):
    try:
        # Initialize the query engine and get the answer
        initialize_summary_settings()

        file_detail = {"name": file_name, "content": pdf_content.file}
        documents = load_multimodal_data(file_detail)

        response = generate_summary(documents)

        logging.debug(f"Response received: {response}")
        return response
        # return {"answer": answer, "chat_history": chat_history}
    except Exception as e:
        logging.error("Error", e)
        raise HTTPException(status_code=500, detail=str(e))