from dotenv import load_dotenv
load_dotenv()
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, StorageContext, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
import nest_asyncio
import os
from pinecone.grpc import PineconeGRPC
from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.retrievers import VectorIndexRetriever, SummaryIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
import time

nest_asyncio.apply()

from data_s3_pdf import download_file
from document_parser import load_multimodal_data

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

def initialize_pinecone_index(index_name):
    api_key = os.environ["PINECONE_API_KEY"]

    pc = PineconeGRPC(api_key=api_key)

    pc.create_index(
        name=index_name,
        dimension=1024, # Replace with your model dimensions
        metric="cosine", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )

    pinecone_index = pc.Index(index_name)

    return pinecone_index

def create_vector_index(index_name, documents):

    api_key = os.environ["PINECONE_API_KEY"]

    pc = PineconeGRPC(api_key=api_key)

    pc.create_index(
        name=index_name,
        dimension=1024, # Replace with your model dimensions
        metric="cosine", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )

    pinecone_index = pc.Index(index_name)

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    pinecone_index.describe_index_stats()

    return index

def initialize_summary_settings():
    
    embed_model = NVIDIAEmbedding(
        model_name="nvidia/nv-embedqa-e5-v5",
        truncate="END",
        nvidia_api_key=os.environ['NVIDIA_API_KEY'])

    Settings.embed_model = embed_model
    Settings.text_splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=0)

def create_summary_index(index_name, documents):

    vector_store = MilvusVectorStore(uri="./milvus_demo.db", dim=1024, overwrite=True) #For CPU only vector store

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = SummaryIndex.from_documents(
        documents, storage_context=storage_context
    )

    return index

initialize_settings()

# initialize_summary_settings()

file_detail = download_file()

documents = load_multimodal_data(file_detail)
index_name = 'vectorindex'
print("Creating index...")
vector_index = create_vector_index(index_name, documents)
print("Vector Store index created")
summary_query_engine = vector_index.as_query_engine(similarity_top_k=10, streaming=True)

print("Loading index into Pinecone...")
time.sleep(120)
print("Pinecone DB updated.")

index_name = 'summaryindex'
print("Creating index...")
summary_index = create_summary_index(index_name, documents)
print("Summary index created")
summary_query_engine = summary_index.as_query_engine()

print("Querying LLM...")
response = summary_query_engine.query("Summarize the document in 200-250 words")
print("Response:", response)