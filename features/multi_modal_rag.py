import streamlit as st
import requests
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
from dotenv import load_dotenv
from parameter_config import FAST_API_DEV_URL

# Load environment variables
load_dotenv()

@st.fragment
def download_fragment(file_content: bytes, file_name: str) -> None:
    st.download_button('**Download File**', file_content, file_name=file_name, key="download_file_button")

def multi_modal_rag():

    print(FAST_API_DEV_URL)
    if 'data_frame' not in st.session_state:
        st.session_state.data_frame = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'history' not in st.session_state:
        st.session_state.history = None
    if 'title' not in st.session_state:
        st.session_state.title = None
    if 'file_path' not in st.session_state:
        st.session_state.file_path = None

    st.title('Multi Modal RAG, Summary and Report Generation App')

    # Fetch data from FastAPI endpoint
    response = requests.get(f"{FAST_API_DEV_URL}/data/get-data/")
    if response.status_code == 200:
        data = response.json()
        st.session_state.data_frame = pd.DataFrame(data)
        
        if not st.session_state.data_frame.empty:
            selected_title = st.selectbox("**Select a PDF Title**:", ["Select a title"] + st.session_state.data_frame['TITLE'].tolist())
            
            if selected_title != "Select a title":
                selected_row = st.session_state.data_frame[st.session_state.data_frame['TITLE'] == selected_title].iloc[0]

                st.session_state.title = selected_row['TITLE']
                # Create columns for layout
                image_col, title_col = st.columns([1, 3])

                # Display the image in the first column
                with image_col:
                    st.image(selected_row['IMAGE_URL'], width=150)
                
                    pdf_url = selected_row['PDF_S3_URL']
                    st.session_state.file_name = pdf_url.split("/")[-1]
                    
                    response_pdf = requests.get(
                        f"{FAST_API_DEV_URL}/data/extract-file/",
                        params={"file_name": st.session_state.file_name},
                        stream=True
                    )

                    if response_pdf.status_code == 200:
                        
                        download_fragment(response_pdf.content, st.session_state.file_name)

                    else:
                        st.error("Failed to download the PDF file.")
                # Display the title and summary in the second column
                with title_col:
                    st.subheader(selected_row['TITLE'])
                    st.write("**Summary**: ", selected_row['BRIEF_SUMMARY'])
                
                chat_col, summary_col, report_col = st.columns(3)

                if chat_col.button("**Chat With PDF**"):
                        st.session_state.chat_with_pdf = True
                        with st.spinner("Creating index..."):

                            data = {
                                "file_name": st.session_state.file_name,
                            }
                            
                            files = {
                                "pdf_content": (st.session_state.file_name, response_pdf.content, "application/pdf")
                            }


                            response_index = requests.post(
                                f"{FAST_API_DEV_URL}/index/create-index/",
                                data=data,
                                files=files
                            )

                            if response_index.status_code == 200:
                                st.success("Index created successfully.")
                            else:
                                st.error(f"Failed to create index. Status code: {response_index.status_code}")
                            st.session_state.history = []
                        st.rerun()
                if summary_col.button("**Generate Summary**"):
                    with st.spinner("Generating summary..."):

                        data = {
                            "file_name": st.session_state.file_name,
                        }
                        
                        files = {
                            "pdf_content": (st.session_state.file_name, response_pdf.content, "application/pdf")
                        }


                        response_summary = requests.get(
                            f"{FAST_API_DEV_URL}/query/generate-summary/",
                            data=data,
                            files=files
                        )

                        if response_summary.status_code == 200:
                            summary = response_summary.json()
                            st.write("**Summary**: ", summary["response"])
                        else:
                            st.error(f"Failed to create index. Status code: {response_summary.status_code}")
                if report_col.button("**Report Based Responses**"):
                    st.session_state.report_generation= True
                    st.session_state.file_path = response_pdf.headers.get("X-File-Path")
                    st.rerun()
                pdf_viewer(input=response_pdf.content,
                        width=700, height=700)
        else:
            st.write("No data available.")
    elif response.status_code == 401:
        st.error("Unauthorized: Invalid data.")
    else:
        st.error(f"An error occurred: {response.status_code} - {response.text}")
