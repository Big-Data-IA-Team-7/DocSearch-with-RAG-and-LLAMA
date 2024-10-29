import pandas as pd
from data_load.data_storage_log import log_success, log_error

def prepare_dataframe(**kwargs):
    try:
        # Pull the DataFrame from XCom
        ti = kwargs['ti']
        df_dict = ti.xcom_pull(task_ids='download_and_upload_files_to_s3', key='s3_uploaded_df')
        df = pd.DataFrame.from_dict(df_dict)

        # Perform any necessary transformations or cleaning on the DataFrame
        # Example: Ensure there are no NaN values in required columns
        df.fillna('', inplace=True)
        log_success("DataFrame prepared for Snowflake upload.")

        # Push the cleaned DataFrame to XCom
        ti.xcom_push(key='prepared_df', value=df.to_dict())

    except Exception as e:
        log_error(f"Error in prepare_dataframe: {e}")
        raise e
