import os
import boto3

from urllib.parse import urlparse, unquote
import requests
import tempfile
from io import BytesIO

def generate_presigned_url(pdf_name, expiration: int = 3600) -> str:
    """
    Generates a pre-signed URL for an S3 object that allows temporary access.

    Args:
        s3_url (str): The S3 URL of the object (e.g., 'https://bucket-name.s3.amazonaws.com/object-key').
        expiration (int, optional): The time in seconds until the pre-signed URL expires. Defaults to 3600 seconds (1 hour).

    Returns:
        str: The pre-signed URL allowing temporary access to the S3 object, or None if an error occurs.
    """
    key = f'pdfs/{pdf_name}'
    
    try:

        s3 = boto3.client('s3',
                  aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

        # Generate pre-signed URL that expires in the given time (default: 1 hour)
        presigned_url = s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': os.environ['AWS_S3_BUCKET_NAME'], 'Key': key},
                                                  ExpiresIn=expiration)
        return presigned_url
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None

def download_file(pdf_name) -> dict:
    """
    Downloads a file from the given URL and saves it as a temporary file with the appropriate extension.

    Args:
        url (str): The URL of the file to be downloaded.

    Returns:
        dict: A dictionary containing the following keys:
            - "url" (str): The original URL of the file.
            - "path" (str): The path to the downloaded temporary file.
            - "extension" (str): The file extension of the downloaded file.
    """
    # Parse the URL to extract the file name
    file_name = generate_presigned_url(pdf_name)
    parsed_url = urlparse(file_name)
    path = unquote(parsed_url.path)
    filename = os.path.basename(path)
    extension = os.path.splitext(filename)[1]

    temp_dir = tempfile.gettempdir()

    # Create a temporary file in the specified directory with the correct extension
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir=temp_dir)

    # Get the file from the URL
    response = requests.get(file_name)
    response.raise_for_status()  # Ensure the request was successful
    file_content = response.content
    
    return {"file_name": filename, "pdf_content": BytesIO(file_content)}