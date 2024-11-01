from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, SummaryIndex, Document
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
import logging

def create_vector_index(pinecone_client, index_name, documents):
    pinecone_client.create_index(
        name=index_name,
        dimension=1024, # Replace with your model dimensions
        metric="cosine", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    pinecone_index = pinecone_client.Index(index_name)

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    return index

def retrieve_query(index_name, user_question, pinecone_client):

    pinecone_index = pinecone_client.Index(index_name)

    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="index_type", operator=FilterOperator.EQ, value="research_index"
            ),
        ]
    )

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    retriever = vector_index.as_retriever(filters=filters)

    response_synthesizer = get_response_synthesizer()

    custom_query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.8)]
    )

    response = custom_query_engine.query(user_question)
    response_text = response.response

    if response_text == "Empty Response":

        summary_query_engine = vector_index.as_query_engine(similarity_top_k=5)

        llm_query = summary_query_engine.query(user_question)
        response_text = llm_query.response

    return response_text

def create_generate_summary(documents):

    vector_store = MilvusVectorStore(uri="./milvus_demo.db", dim=1024, overwrite=True) #For CPU only vector store

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    summary_index = SummaryIndex.from_documents(
        documents, storage_context=storage_context
    )

    summary_query_engine = summary_index.as_query_engine()

    response = summary_query_engine.query("Summarize the document in 200-250 words")

    return response

def research_index_create(index_name, pinecone_client, question_answer):

    pinecone_index = pinecone_client.Index(index_name)

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    research_metadata = {
        "index_type": "research_index"
    }

    doc = Document(text=question_answer, metadata=research_metadata)

    vector_index.insert(doc)

    return vector_index