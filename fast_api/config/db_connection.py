# snowflake_connect.py
# from project_logging import logging_module
import snowflake.connector
import os
from dotenv import load_dotenv 

# Load environment variables from .env file (if applicable)
load_dotenv()

def create_snowflake_connection():
    """Creates and returns a Snowflake connection."""
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),  # e.g., 'your_account_name.region.cloud_provider'
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        role=os.getenv('SNOWFLAKE_ROLE')  # optional, if you need a specific role
    )
    return conn

def close_my_sql_connection(mydb, mydata = None):
    try:
        if mydb.is_connected():
            mydata.close()
            mydb.close()
            print('Snowflake connection is closed')
            # logging_module.log_success("MySQL connection closed.")
    except Exception as e:
        print(f"Error closing the MySQL connection: {e}")
        # logging_module.log_error(f"Error closing the MySQL connection: {e}")