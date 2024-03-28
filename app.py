import streamlit as st
import requests
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from src.prepare_vector_db import create_db_from_text
from src.qabot import answer

API_URL = "https://api-inference.huggingface.co/models/nguyenvulebinh/vi-mrc-base"
headers = {"Authorization": "Bearer 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"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def main() -> None:
    st.set_page_config(page_title="Ask your PDF")
    st.header("Trò chuyện với file PDF 💬")

    # upload file
    pdf = st.file_uploader("Upload file PDF", type="pdf")

    # extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # # Create vector DB
        # create_db_from_text(text)

        # show user input
        ''' Ví dụ:
        Tổ chức Đoàn TNCS Hồ Chí Minh thành lập ngày nào?
        '''
        user_question = st.text_input("Mời bạn đặt câu hỏi:")
        if user_question:
            response = query({
                "inputs": {
                    "question": f"{user_question}",
                    "context": f"{text}"
                },
            })
            st.write(
                f"Câu trả lời mà chúng tôi tìm được: {response['answer']}")


if __name__ == "__main__":
    main()
