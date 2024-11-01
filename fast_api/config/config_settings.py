import os

from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from pinecone.grpc import PineconeGRPC

# snowflake_connect.py
import snowflake.connector
from dotenv import load_dotenv 
# Load environment variables from .env file (if applicable)
load_dotenv()


def initialize_settings():
    
    embed_model = NVIDIAEmbedding(
        model_name="nvidia/nv-embedqa-e5-v5",
        truncate="END",
        nvidia_api_key=os.environ['NVIDIA_API_KEY'])
    
    llm = NVIDIA(
        model="meta/llama-3.1-405b-instruct",
        nvidia_api_key=os.environ['NVIDIA_API_KEY'])
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.text_splitter = SentenceSplitter(chunk_size=600)

def initialize_summary_settings():
    
    embed_model = NVIDIAEmbedding(
        model_name="nvidia/nv-embedqa-e5-v5",
        truncate="END",
        nvidia_api_key=os.environ['NVIDIA_API_KEY'])

    Settings.embed_model = embed_model
    Settings.llm = OpenAI()
    Settings.text_splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=0)

def get_pinecone_client():
    api_key = os.environ["PINECONE_API_KEY"]

    pc = PineconeGRPC(api_key=api_key)

    return pc

def create_snowflake_connection():
    """Creates and returns a Snowflake connection."""
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        role=os.getenv('SNOWFLAKE_ROLE') 
    )
    return conn

def close_my_sql_connection(mydb, mydata = None):
    try:
        if mydb.is_connected():
            mydata.close()
            mydb.close()
            print('Snowflake connection is closed')
    except Exception as e:
        print(f"Error closing the MySQL connection: {e}")