from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

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


def query_vector_index(index_name, user_question, pinecone_client):

    pinecone_index = pinecone_client.Index(index_name)

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    summary_query_engine = vector_index.as_query_engine(similarity_top_k=5)

    llm_query = summary_query_engine.query(user_question)

    return llm_query.response