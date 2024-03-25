import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from src.prepare_vector_db import create_db_from_text
from src.qabot import answer


def main() -> None:
    st.set_page_config(page_title="Ask your PDF")
    st.header("Ask your PDF 💬")

    # upload file
    pdf = st.file_uploader("Upload your PDF", type="pdf")

    # extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Create vector DB
        create_db_from_text(text)

        # show user input
        user_question = st.text_input("Ask a question about your PDF:")
        if user_question:
            response = answer(user_question)
            st.write(response)


if __name__ == "__main__":
    main()
