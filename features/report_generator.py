import streamlit as st
import requests
from PIL import Image
from pydantic import TypeAdapter
from fast_api.schemas.report_schema import ReportOutput, TextBlock, ImageBlock
from parameter_config import FAST_API_DEV_URL

def render_streamlit(blocks):
    """Render blocks in Streamlit."""
    for b in blocks:
        if 'text' in b:
            # Display text as markdown
            st.markdown(b['text'])
        elif 'file_path' in b:
            # Display image
            image = Image.open(b['file_path'])
            st.image(image)

def generate_report():
    st.title(f"Report Generation With {st.session_state.title}")
    question = st.text_input("Enter your question:")

    if st.button("Generate Report"):
            params = {
                "file_name": st.session_state.file_name,
                "file_path": st.session_state.file_path,
                "user_input": question
            }
            response = requests.get(
                f"{FAST_API_DEV_URL}/query/generate-report/",
                params=params
            )
            if response.status_code == 200:
                # Parse the JSON response

                report_output = TypeAdapter(ReportOutput).validate_python(response.json())
                

                # Display each block in Streamlit
                for block in report_output.blocks:
                    if isinstance(block, TextBlock):
                        # Display text as markdown in Streamlit
                        st.markdown(block.text)
                    elif isinstance(block, ImageBlock):
                        # Display image from file path in Streamlit
                        st.image(block.file_path)