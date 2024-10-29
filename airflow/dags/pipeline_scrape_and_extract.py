from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from data_load.scrape_data import scrape_data
from data_load.download_and_upload_files_to_s3 import download_and_upload_files_to_s3
from data_load.upload_to_s3 import upload_files_to_s3
from data_load.prepare_dataframe import prepare_dataframe
from data_load.load_to_snowflake import load_dataframe_to_snowflake
import os
from dotenv import load_dotenv

# Load environment variables 
load_dotenv()

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


# Define the DAG
with DAG(
    'cfa_scraper_dag',
    default_args=default_args,
    description='A DAG to scrape CFA Institute data, store files in S3, and load into Snowflake',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Scrape data
    scrape_data_task = PythonOperator(
        task_id='scrape_data',
        python_callable=scrape_data,
        provide_context=True,
    )

    # Task 2: Download files
    download_and_upload_task = PythonOperator(
        task_id='download_and_upload_files_to_s3',
        python_callable=download_and_upload_files_to_s3,
        provide_context=True,
    )

    # Task 4: Prepare DataFrame with S3 URLs
    prepare_dataframe_task = PythonOperator(
        task_id='prepare_dataframe',
        python_callable=prepare_dataframe,
        provide_context=True,
    )

    # Task 5: Load DataFrame into Snowflake
    load_to_snowflake_task = PythonOperator(
        task_id='load_to_snowflake',
        python_callable=load_dataframe_to_snowflake,
        provide_context=True,
    )

    # Set task dependencies
    scrape_data_task >> download_and_upload_task >> prepare_dataframe_task >> load_to_snowflake_task