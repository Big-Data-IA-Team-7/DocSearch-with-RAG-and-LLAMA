import snowflake.connector
import pandas as pd
import os
from data_load.data_storage_log import log_success, log_error
from data_load.parameter_config import SNOWFLAKE_ACCOUNT, SNOWFLAKE_DATABASE, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, SNOWFLAKE_SCHEMA, SNOWFLAKE_USER, SNOWFLAKE_WAREHOUSE 

def load_dataframe_to_snowflake(**kwargs):
    try:
        # Pull the prepared DataFrame from XCom
        ti = kwargs['ti']
        df_dict = ti.xcom_pull(task_ids='prepare_dataframe', key='prepared_df')
        df = pd.DataFrame.from_dict(df_dict)
        print(df)

        # Connect to Snowflake using credentials from environment variables
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            role=SNOWFLAKE_ROLE
        )

        cursor = conn.cursor()

        # Create table if it does not exist (adjust the SQL for your schema)
        create_table_sql = """
        CREATE OR REPLACE TABLE pdf_metadata_table (
            Title STRING,
            Image_URL STRING,
            Brief_Summary STRING,
            Summary_Page_Link STRING,
            PDF_S3_URL STRING,
            Image_S3_URL STRING
        )
        """
        cursor.execute(create_table_sql)

        # Insert data into the Snowflake table
        for i, row in df.iterrows():
            insert_sql = """
            INSERT INTO pdf_metadata_table (
                Title, Image_URL, Brief_Summary, Summary_Page_Link, PDF_S3_URL, Image_S3_URL
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                row['Title'],
                row['Image_URL'],
                row['Brief_Summary'],
                row['Summary_Page_Link'],
                row['PDF_S3_URL'],
                row['Image_S3_URL']
            ))

        conn.commit()
        log_success("Data successfully loaded into Snowflake.")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        log_error(f"Error in load_dataframe_to_snowflake: {e}")
        raise e
