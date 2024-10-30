import os

from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from pinecone.grpc import PineconeGRPC

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
    Settings.text_splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=0)

def initalize_pinecone_object():
    api_key = os.environ["PINECONE_API_KEY"]

    pc = PineconeGRPC(api_key=api_key)

    return pc