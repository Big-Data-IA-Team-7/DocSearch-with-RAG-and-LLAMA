import os
import streamlit as st
import requests
import pandas as pd
import base64
from dotenv import load_dotenv
from openai import OpenAI

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

    if 'data_frame' not in st.session_state:
        st.session_state.data_frame = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'index' not in st.session_state:
        st.session_state.index = None
    if 'history' not in st.session_state:
        st.session_state.history = None
    if 'title' not in st.session_state:
        st.session_state.title = None

    st.title('Multi Modal RAG')

    # Fetch data from FastAPI endpoint
    response = requests.get(f"{os.getenv('FASTAPI_DEV_URL')}/data/get-data/")
    if response.status_code == 200:
        data = response.json()
        st.session_state.data_frame = pd.DataFrame(data)
        
        if not st.session_state.data_frame.empty:
            selected_title = st.selectbox("Select a PDF Title:", ["Select a title"] + st.session_state.data_frame['TITLE'].tolist())
            
            if selected_title != "Select a title":
                selected_row = st.session_state.data_frame[st.session_state.data_frame['TITLE'] == selected_title].iloc[0]

                st.session_state.title = selected_row['TITLE']
                # Create columns for layout
                col1, col2 = st.columns([1, 3])

                # Display the image in the first column
                with col1:
                    st.image(selected_row['IMAGE_URL'], width=150)
                
                    pdf_url = selected_row['PDF_S3_URL']
                    st.session_state.file_name = pdf_url.split("/")[-1]
                    
                    response_pdf = requests.get(
                        f"{os.getenv('FASTAPI_DEV_URL')}/data/extract-file/",
                        params={"file_name": st.session_state.file_name},
                        stream=True
                    )

                    if response_pdf.status_code == 200:

                        download_fragment(response_pdf.content, st.session_state.file_name)

                    else:
                        st.error("Failed to download the PDF file.")
                # Display the title and summary in the second column
                with col2:
                    st.subheader(selected_row['TITLE'])
                    st.write("**Summary**: ", selected_row['BRIEF_SUMMARY'])

                    if st.button("**Chat With PDF**"):
                        st.session_state.chat_with_pdf = True
                        with st.spinner("Creating index..."):

                            data = {
                                "file_name": st.session_state.file_name,
                            }
                            
                            files = {
                                "pdf_content": (st.session_state.file_name, response_pdf.content, "application/pdf")
                            }


                            response_index = requests.post(
                                f"{os.getenv('FASTAPI_DEV_URL')}/index/create-index/",
                                data=data,
                                files=files
                            )

                            if response_index.status_code == 200:
                                st.success("Index created successfully.")
                            else:
                                st.error(f"Failed to create index. Status code: {response_index.status_code}")
                            st.session_state.history = []
                        st.rerun()
                    if st.button("**Generate Summary**"):
                        with st.spinner("Generating summary..."):

                            data = {
                                "file_name": st.session_state.file_name,
                            }
                            
                            files = {
                                "pdf_content": (st.session_state.file_name, response_pdf.content, "application/pdf")
                            }


                            response_summary = requests.get(
                                f"{os.getenv('FASTAPI_DEV_URL')}/query/generate-summary/",
                                data=data,
                                files=files
                            )

                            if response_summary.status_code == 200:
                                summary = response_summary.json()
                                st.write("**Summary**: ", summary["response"])
                            else:
                                st.error(f"Failed to create index. Status code: {response_summary.status_code}")
        else:
            st.write("No data available.")
    elif response.status_code == 401:
        st.error("Unauthorized: Invalid data.")
    else:
        st.error(f"An error occurred: {response.status_code} - {response.text}")
