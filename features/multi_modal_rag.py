import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from document_processors import load_multimodal_data

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")  # Replace with your actual API key
)

# Prompt for generating summaries
system_prompt = """\
You are a summary generation assistant tasked with producing a well-formatted general summary based on parsed text.
You will be given content from one or more reports that take the form of parsed text. Your responsibility is to generate a concise and coherent summary that captures the key points and insights from the provided text.
Ensure that the summary is clear and integrated without including any references to images or visual elements.
Output your response as a tool call to adhere to the required output format. Do NOT provide normal text.
"""

# Function to generate summaries
def generate_summary(content):
    completion = client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": system_prompt}, {"role": "user", "content": content}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )
    
    summary = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            summary += chunk.choices[0].delta.content
    return summary

@st.fragment
def download_fragment(file_content: bytes, file_name: str) -> None:
    st.download_button('**Download File**', file_content, file_name=file_name, key="download_file_button")

def multi_modal_rag():
    st.title('Multi Modal RAG')

    # Fetch data from FastAPI endpoint
    response = requests.get(f"{os.getenv('FASTAPI_DEV_URL')}/data/get-data/")
    if response.status_code == 200:
        data = response.json()
        data_df = pd.DataFrame(data)
        
        if not data_df.empty:
            selected_title = st.selectbox("Select a PDF Title:", ["Select a title"] + data_df['TITLE'].tolist())
            
            if selected_title != "Select a title":
                selected_row = data_df[data_df['TITLE'] == selected_title].iloc[0]

                # Create columns for layout
                col1, col2 = st.columns([1, 3])

                # Display the image in the first column
                with col1:
                    st.image(selected_row['IMAGE_URL'], width=150)
                
                    pdf_url = selected_row['PDF_S3_URL']
                    filename = pdf_url.split("/")[-1]
                    
                    response_pdf = requests.get(
                        f"{os.getenv('FASTAPI_DEV_URL')}/data/extract-file/",
                        params={"file_name": filename},
                        stream=True  # Set stream=True to handle large files efficiently
                    )

                    if response_pdf.status_code == 200:

                        download_fragment(response_pdf.content, filename)

                    else:
                        st.error("Failed to download the PDF file.")
                # Display the summary in the second column
                with col2:
                    st.subheader(selected_row['TITLE'])
                    st.write("**Summary**: ", selected_row['BRIEF_SUMMARY'])

                    if st.button("**Chat With PDF**"):
                        st.warning("Please upload a document first!")

        else:
            st.write("No data available.")
    elif response.status_code == 401:
        st.error("Unauthorized: Invalid data.")
    else:
        st.error(f"An error occurred: {response.status_code} - {response.text}")
