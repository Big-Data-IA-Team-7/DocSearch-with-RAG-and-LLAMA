from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fast_api.config.config_settings import get_pinecone_client
from fast_api.services.rag_service import retrieve_query, create_generate_summary
from fast_api.services.report_service import report_generate
from fast_api.services.data_service import download_file
from fast_api.config.config_settings import initialize_settings, initialize_summary_settings
from fast_api.services.multi_modal.document_parser import load_multimodal_data
from fastapi.responses import JSONResponse
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
        response_text = retrieve_query(file_name, user_question, pinecone_client)
        logging.debug(f"Response received: {response_text}")
        return response_text
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