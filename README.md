# DocSearch-with-RAG-and-LLAMA

## Overview

A comprehensive data ingestion and document exploration application using **FastAPI** and **Streamlit**. This project scrapes data from the CFA Institute Research Foundation Publications, stores data in AWS S3 and Snowflake, and provides an intuitive interface for document browsing, summary generation, and Q&A interaction with a multi-modal Retrieval-Augmented Generation (RAG) model.

## Project Resources

- **Google Codelab**: [Codelab Link](https://codelabs-preview.appspot.com/?file_id=19PUe2WgvP52FTphLPKi-rW8FkJG_d2xorLtYUDuqm38/edit?tab=t.0#0)
- **App (Deployed on AWS EC2)**: [Streamlit Link](http://75.101.133.31:8501/)
- **Airflow (Deployed on AWS EC2)**: [Airflow Link](http://75.101.133.31:8080/)
- **YouTube Demo**: [Demo Link](https://www.youtube.com/watch?v=yKyeI7d-krM)

## Features

### Data Ingestion and Database Population
- **Scraping Data**: Extracts publication details (title, image, summary, PDF) from the CFA Institute Research Foundation.
- **Storage in S3**: Images and PDFs are uploaded to AWS S3.
- **Database in Snowflake**: Metadata (title, summary, S3 links) is stored in Snowflake for easy access and querying.

### Client-Facing Application
- **FastAPI Endpoints**: Provides API access to explore and interact with the stored documents.
- **Streamlit UI**: Enables users to browse documents via an image grid or dropdown selection.
- **Summary and Q&A Interface**: Generates summaries and supports document-based Q&A using NVIDIA multi-modal RAG models.

### Research Notes Indexing and Search
- **Incremental Indexing**: Automatically indexes research notes for efficient querying.
- **Advanced Search**: Allows search within research notes or full documents for specific queries.

## Architecture

The application includes the following main components:
1. **Data Ingestion Pipeline**: Automated with Airflow for scraping and loading data into AWS S3 and Snowflake.
2. **FastAPI Backend**: Exposes APIs for document exploration, summary generation, and Q&A interaction.
3. **Streamlit Frontend**: Provides a user-friendly interface for document browsing, selection, and Q&A.
4. **RAG Indexing**: Utilizes a multi-modal RAG model to enable efficient and context-aware document querying.

## Technologies

- **Python**: Core programming language
- **FastAPI**: API development
- **Streamlit**: Interactive frontend
- **Snowflake**: Database for metadata storage
- **AWS S3**: Storage for images and PDFs
- **Airflow**: Data ingestion and automation
- **Docker**: Containerization
- **NVIDIA Multi-modal RAG**: Document interaction and Q&A
- **GitHub Issues**: Task tracking and management

## Architecture Diagram

![Architecture Diagram]

For Airflow Orchestration

<img width="734" alt="image" src="https://github.com/user-attachments/assets/e84a7006-176f-41eb-8f98-d9b4d3736d6c">


For FastAPI

<img width="716" alt="image" src="https://github.com/user-attachments/assets/607444ea-dd83-42e5-be23-dbf8a5815968">


---


## How to Run the Application


### Clone the Repository

```bash
# Clone the Repository
git clone https://github.com/Big-Data-IA-Team-7/DocSearch-with-RAG-and-LLAMA
cd DocSearch-with-RAG-and-LLAMA

# Update Parameter Store with Your Keys and Set Up IAM Access
# Replace placeholders with your actual AWS and OpenAI keys
ACCESS_KEY_ID_AWS=<your-access-key-id>
SECRET_ACCESS_KEY_AWS=<your-secret-access-key>
OPEN_AI_API_KEY=<your-open-ai-api-key>

# Dockerize the Application
docker build -t ramkumarrp16077/airflow-image-2:latest .
docker push ramkumarrp16077/airflow-image-2:latest

# Set Up EC2 Instance and Install Prerequisites
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Log in to Docker
docker login
docker pull ramkumarrp16077/airflow-image-2:latest

# Run the Application
docker run -d -p 8080:8080 ramkumarr16077/airflow-image-2:latest
```


## Contributions

| Name                        | Contribution                                                                                                     |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------|
| Pragnesh Anekal             | 33% - Building FastAPI end points, generate Summary, Report Generation, Creating Pinecone Index  , Deploying Streamlit and FastAPI  |
| Ram Kumar Ramasamy Pandiaraj| 33% - Web Scraping, Parsing the data, loading into S3 and Snowflake , Building and deploying Airflow Pipeline       |
| Dipen Manoj Patel           | 33% - Summary Generation, Vector Index, Setting up Milvus, Streamlit Front End, Deploying Streamlit |



## Attestation

**WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.**



