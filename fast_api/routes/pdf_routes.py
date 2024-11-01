from fastapi import APIRouter, HTTPException
from fast_api.services.data_service import download_file

router = APIRouter()

@router.get("/select_pdf/{file_name}")
def select_pdf(file_name: str):
    try:
        # Retrieve PDF from S3
        selected_file = download_file(file_name)
        return selected_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))