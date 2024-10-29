import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from document_processors import load_multimodal_data
import json

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

def Home():
    st.title('RAG BASED Multi Model')

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
                col1, col2 = st.columns([1, 2])  # Adjust column width ratios as needed

                # Display the image in the first column
                with col1:
                    st.image(selected_row['IMAGE_URL'], width=250)
                    st.subheader(selected_row['TITLE'])
                
                    pdf_url = selected_row['PDF_S3_URL']
                    response_pdf = requests.get(f"{os.getenv('FASTAPI_DEV_URL')}/data/view_s3_url/?url={pdf_url}")
                    if response_pdf.status_code == 200:
                        data = response_pdf.json()
                        presigned_url = data['url']  # Extract the presigned URL

                        # Use Streamlit's download button to download the PDF
                        st.download_button(
                            label="Download PDF",
                            data=requests.get(presigned_url).content,
                            file_name=selected_row["PDF_S3_URL"].split("/")[-1],
                            mime="application/pdf"
                        )



                # Display the summary in the second column
                with col2:
                    uploaded_file = st.file_uploader("Upload a document for summarization", type=["pdf", "png", "jpg", "jpeg", "ppt", "pptx"])

                    if uploaded_file is not None:
                        with st.spinner("Processing your file..."):
                            documents = load_multimodal_data([uploaded_file])  # Process the uploaded file
                            content = "\n\n".join(doc.text for doc in documents)
                            summary = generate_summary(content)
                            st.subheader("Generated Summary")
                            st.markdown(summary)
                            st.success("Summary generated successfully!")

                    if st.button("Summarize"):
                        st.warning("Please upload a document first!")

        else:
            st.write("No data available.")
    elif response.status_code == 401:
        st.error("Unauthorized: Invalid data.")
    else:
        st.error(f"An error occurred: {response.status_code} - {response.text}")
