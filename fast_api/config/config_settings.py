import os

from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from pinecone.grpc import PineconeGRPC
from parameter_config import NVIDIA_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_SCHEMA, SNOWFLAKE_DATABASE, SNOWFLAKE_ROLE, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_ACCOUNT

# snowflake_connect.py
import snowflake.connector
from dotenv import load_dotenv 
# Load environment variables from .env file (if applicable)
load_dotenv()


def initialize_settings():
    
    embed_model = NVIDIAEmbedding(
        model_name="nvidia/nv-embedqa-e5-v5",
        truncate="END",
        nvidia_api_key=NVIDIA_API_KEY)
    
    llm = NVIDIA(
        model="meta/llama-3.1-405b-instruct",
        nvidia_api_key=NVIDIA_API_KEY)
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.text_splitter = SentenceSplitter(chunk_size=600)

def initialize_summary_settings():
    
    embed_model = NVIDIAEmbedding(
        model_name="nvidia/nv-embedqa-e5-v5",
        truncate="END",
        nvidia_api_key=NVIDIA_API_KEY)

    Settings.embed_model = embed_model
    Settings.llm = OpenAI(api_key=OPENAI_API_KEY)
    Settings.text_splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=0)

def get_pinecone_client():
    api_key = PINECONE_API_KEY

    pc = PineconeGRPC(api_key=api_key)

    return pc

def create_snowflake_connection():
    """Creates and returns a Snowflake connection."""
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE 
    )
    return conn