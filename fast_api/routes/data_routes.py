from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from services.data_service import fetch_data_from_db,parse_s3_url,download_pdf_from_s3,generate_presigned_url
import pandas as pd
from typing import List, Dict
import os
# from project_logging import logging_module

router = APIRouter()

@router.get("/get-data/", response_model=List[dict])
def get_data():
    # Fetch data from the database
    data = fetch_data_from_db()
    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No data returned from the database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.get("/download_s3_url/",response_model=List[dict])
async def download_s3_url(url: str):
    target_bucket = os.getenv('AWS_S3_BUCKET_NAME')

    bucket, key = parse_s3_url(url)

    # Check if the URL is from the correct bucket and located in the "pdfs" folder
    if bucket == target_bucket and key.startswith("pdfs/") and key.endswith(".pdf"):
        local_file_name = key.split('/')[-1]  # Use the file name from the key
        try:
            downloaded_file = download_pdf_from_s3(bucket, key, local_file_name)
            return JSONResponse(content={"message": f"Downloaded {downloaded_file} from S3 bucket {bucket}."})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Skipping non-PDF or non-target URL.")
    
    
@router.get("/view_s3_url/", response_model=dict)
async def view_s3_url(url: str):
    target_bucket = os.getenv('AWS_S3_BUCKET_NAME')

    bucket, key = parse_s3_url(url)

    # Check if the URL is from the correct bucket and located in the "pdfs" folder
    if bucket == target_bucket and key.startswith("pdfs/") and key.endswith(".pdf"):
        try:
            # Generate a pre-signed URL for viewing
            presigned_url = generate_presigned_url(bucket, key)
            return {"url": presigned_url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating pre-signed URL: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Skipping non-PDF or non-target URL.")



