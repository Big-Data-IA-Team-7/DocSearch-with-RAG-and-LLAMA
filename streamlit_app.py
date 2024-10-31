import streamlit as st
from features.multi_modal_rag import multi_modal_rag

# Set up the page configuration
rag_page = st.Page(multi_modal_rag, title="Multi Modal RAG", icon=":material/book:")
# st.set_page_config(page_title="Multi Modal RAG", page_icon=":material/book:", layout="wide")

# Call your multi_modal_rag function to render the app
# multi_modal_rag()

pg = st.navigation([rag_page])

# Set Configurations
st.set_page_config(page_title="My Application", page_icon=":material/lock:")

# Run the selected page
pg.run()



