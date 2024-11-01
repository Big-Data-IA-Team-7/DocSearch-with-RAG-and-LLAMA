from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, SummaryIndex, Document
from llama_index.vector_stores.milvus import MilvusVectorStore
from typing import List, Tuple
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from fast_api.schemas.hybrid_schema import CustomRetriever

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

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

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

# def retrieve_query_workflow(index_name, user_question, pinecone_client, document_ids: List[str]) -> Tuple[str, List[NodeWithScore]]:
#     # Initialize Pinecone index and VectorStore
#     pinecone_index = pinecone_client.Index(index_name)
#     vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

#     # Initialize the vector index from the vector store
#     vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

#     # Set up the retrievers for filtered and unfiltered queries
#     vector_retriever_all = VectorIndexRetriever(index=vector_index, similarity_top_k=5)
#     vector_retriever_filtered = CustomRetriever(
#         vector_retriever=vector_retriever_all,
#         document_ids=set(document_ids)
#     )

#     # Define query engines
#     filtered_query_engine = RetrieverQueryEngine(retriever=vector_retriever_filtered)
#     full_query_engine = RetrieverQueryEngine(retriever=vector_retriever_all)

#     # Create the query bundle
#     query_bundle = QueryBundle(user_question)

#     # Perform the initial query on the filtered document set
#     filtered_response = filtered_query_engine.query(query_bundle)
#     if filtered_response and filtered_response.response and filtered_response.similarity_score >= 0.7:
#         # If similarity score >= 0.7, return filtered response
#         response_text = filtered_response.response
#         retrieved_docs = [doc for doc in filtered_response.documents]
#         return response_text, retrieved_docs
#     else:
#         # If similarity score < 0.7, query across all documents
#         full_response = full_query_engine.query(query_bundle)
#         response_text = full_response.response
#         retrieved_docs = [doc for doc in full_response.documents]
#         return response_text, retrieved_docs