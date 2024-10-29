from dotenv import load_dotenv
load_dotenv()
import os

import nest_asyncio

nest_asyncio.apply()

from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from s3reader import S3Reader
from llama_index.embeddings.nvidia import NVIDIAEmbedding

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Set up parser
parser = LlamaParse(
    api_key=os.environ['LLAMA_CLOUD_API_KEY'],
    result_type="markdown",  # "markdown" and "text" are available
    verbose=True
)

# Set up embedder
embedder = NVIDIAEmbedding(model="NV-Embed-QA")

file_extractor = {".pdf": parser}

key='pdfs/0_document.pdf'

loader = S3Reader(
    bucket=os.environ['AWS_S3_BUCKET_NAME'],
    key=key,
    file_extractor=file_extractor,
    aws_access_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_access_secret=os.environ['AWS_SECRET_ACCESS_KEY'],
)

print("connected")

# List of documents loaded from s3
documents = loader.load_data()

print(len(documents))
print(documents[0])