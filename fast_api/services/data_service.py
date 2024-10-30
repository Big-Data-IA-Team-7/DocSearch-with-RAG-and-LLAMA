# data_retrieval.py
import snowflake.connector
from config.db_connection import close_my_sql_connection, create_snowflake_connection
import pandas as pd
import boto3
from urllib.parse import urlparse, unquote
import os
import requests
import tempfile
from dotenv import load_dotenv 
from botocore.exceptions import NoCredentialsError

# Load environment variables from .env file (if applicable)
load_dotenv()

# from project_logging import logging_module

def fetch_data_from_db() -> pd.DataFrame:
    """
    Fetches data from the 'user login' table in the MySQL database and returns it as a pandas DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the data fetched from the database, or None if an error occurs.
    """
    mydata = None  # Initialize mydata to None
    mydb = None    # Initialize mydb to None
    try:
        # Connect to snowflake database
        mydb = create_snowflake_connection()
        
        # logging_module.log_success("Connected to the database for fetching data.")
        print("Connected to the database for fetching data.")
        # Create a cursor object
        mydata = mydb.cursor()

        # Execute the query
        mydata.execute("SELECT * FROM edw.pdf_metadata_table")
        
        # Fetch all the data
        myresult = mydata.fetchall()

        # logging_module.log_success("Fetched data from edw.pdf_metadata_table")
        print("Fetched data from edw.pdf_metadata_table")
        # Get column names
        columns = [col[0] for col in mydata.description]

        # Store the fetched data into a pandas DataFrame
        df = pd.DataFrame(myresult, columns=columns)

        return df

    except snowflake.connector.Error as e:
        # logging_module.log_error(f"Database error occurred: {e}")
        print(f"Database error occurred: {e}")
        return None

    except Exception as e:
        # logging_module.log_error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
        return None

    finally:
        # Ensure that the cursor and connection are properly closed
        close_my_sql_connection(mydb, mydata)


def fetch_pdf_urls_from_snowflake():
    conn=create_snowflake_connection()
    
    query = "SELECT PDF_S3_URL FROM edw.pdf_metadata_table;"
    cursor = conn.cursor()
    cursor.execute(query)
    
    pdf_urls = cursor.fetchall()  # Returns list of tuples
    cursor.close()
    conn.close()
    
    return [url[0] for url in pdf_urls]  # Extract URL from tuple


def parse_s3_url(s3_url):
    if s3_url.startswith('s3://'):
        # For 's3://' format
        parsed_url = urlparse(s3_url)
        bucket = parsed_url.netloc
        key = parsed_url.path.lstrip('/')
    else:
        # For 'https://' format (if needed in future)
        parsed_url = urlparse(s3_url)
        bucket = parsed_url.netloc.split('.')[0]  # Get the bucket name from the URL
        key = parsed_url.path.lstrip('/')
    
    return bucket, key

def download_pdf_from_s3(bucket, key, local_file_name):
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    # Download the file
    s3.download_file(bucket, key, local_file_name)
    print(f"Downloaded {local_file_name} from S3 bucket {bucket}.")


# def generate_presigned_url(bucket_name: str, object_key: str, expiration: int = 3600) -> str:
#     s3_client = boto3.client('s3')
#     try:
#         response = s3_client.generate_presigned_url('get_object',
#             Params={'Bucket': bucket_name, 'Key': object_key},
#             ExpiresIn=expiration)
#         return response
#     except NoCredentialsError:
#         raise Exception("Credentials not available.")


def generate_presigned_url(bucket_name: str, object_key: str, expiration: int = 3600) -> str:
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                'ResponseContentDisposition': 'inline'  # Ensure the content is displayed inline
            },
            ExpiresIn=expiration
        )
        return response
    except NoCredentialsError:
        raise Exception("Credentials not available.")
    except Exception as e:
        raise Exception(f"Error generating presigned URL: {str(e)}")