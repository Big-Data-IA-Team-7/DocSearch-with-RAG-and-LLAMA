import pandas as pd
import requests
import os
import boto3
from botocore.config import Config
from data_load.data_storage_log import log_success, log_error
from num2words import num2words
from data_load.parameter_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME

def create_s3_client():
    """Create an S3 client using AWS credentials from environment variables."""
    try:
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    except Exception as e:
        log_error(f"Error connecting to S3: {e}")
        return

    return s3_client

def download_file(url, file_path):
    """Download a file from a URL and save it to the given file path."""
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        content_length = response.headers.get('Content-Length')
        if content_length is None or int(content_length) == 0:
            log_error(f"Downloaded content for '{url}' is empty.")
            return None

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return file_path
    except Exception as e:
        log_error(f"Failed to download file from {url}: {e}")
        return None

def upload_to_s3(s3_client, file_name, bucket, object_name):
    """Upload a local file to an S3 bucket and return the S3 URL."""
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        s3_url = f"https://{bucket}.s3.amazonaws.com/{object_name}"
        return s3_url
    except Exception as e:
        log_error(f"Failed to upload file to S3: {e}")
        return None

def process_and_store_in_s3(df, s3_client, s3_bucket):
    """Download PDFs and images, upload to S3, and update DataFrame with S3 URLs."""
    base_url = "https://rpc.cfainstitute.org"

    for idx, row in df.iterrows():
        title = row.get('Title', f"Document_{idx}")

        # Process PDF
        pdf_link = row.get('PDF_Link')
        if pdf_link:
            if not pdf_link.startswith('http'):
                pdf_link = base_url + pdf_link
            log_success(f"Extracted PDF link for '{title}': {pdf_link}")

            idx_name = num2words(int(idx)+1)
            idx_name = idx_name.strip().replace("-","")
            
            pdf_file_path = f"/tmp/document{idx_name}.pdf"
            downloaded_pdf = download_file(pdf_link, pdf_file_path)
            if downloaded_pdf:
                pdf_s3_key = f"pdfs/document{idx_name}.pdf"
                pdf_s3_url = upload_to_s3(s3_client, downloaded_pdf, s3_bucket, pdf_s3_key)
                df.at[idx, 'PDF_S3_URL'] = pdf_s3_url
                log_success(f"Successfully uploaded PDF for '{title}' to S3 at {pdf_s3_url}")
                os.remove(pdf_file_path)  # Clean up temporary file

        # Process Image
        image_url = row.get('Image_URL')
        if image_url:
            log_success(f"Extracted Image URL for '{title}': {image_url}")

            idx_name = num2words(int(idx)+1)
            idx_name = idx_name.strip().replace("-","")

            image_file_path = f"/tmp/image{idx_name}.jpg"
            downloaded_image = download_file(image_url, image_file_path)
            if downloaded_image:
                image_s3_key = f"images/image{idx_name}.jpg"
                image_s3_url = upload_to_s3(s3_client, downloaded_image, s3_bucket, image_s3_key)
                df.at[idx, 'Image_S3_URL'] = image_s3_url
                log_success(f"Successfully uploaded image for '{title}' to S3 at {image_s3_url}")
                os.remove(image_file_path)  # Clean up temporary file

    return df

def download_and_upload_files_to_s3(**kwargs):
    try:
        # Pull the DataFrame from XCom
        ti = kwargs['ti']
        df_dict = ti.xcom_pull(task_ids='scrape_data')
        df = pd.DataFrame.from_dict(df_dict)

        # Initialize S3 client
        s3_client = create_s3_client()
        s3_bucket_name = AWS_S3_BUCKET_NAME

        # Process and upload files, updating DataFrame with S3 URLs
        df = process_and_store_in_s3(df, s3_client, s3_bucket_name)

        # Push the updated DataFrame to XCom
        ti.xcom_push(key='s3_uploaded_df', value=df.to_dict())
        log_success("Pushed updated DataFrame to XCom with S3 URLs.")

    except Exception as e:
        log_error(f"Error in download_and_upload_files_to_s3: {e}")
        raise e