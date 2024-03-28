import streamlit as st
import requests
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from src.prepare_vector_db import create_db_from_text
from src.qabot import answer
import time

API_URL = "https://api-inference.huggingface.co/models/nguyenvulebinh/vi-mrc-base"
headers = {"Authorization": "Bearer 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"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def response_generator(response: str):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def main() -> None:
    st.set_page_config(page_title="Ask your PDF")
    st.title("Trò chuyện với file PDF")

    st.header("Bước 1: Upload file PDF 📤")
    # upload file
    pdf = st.file_uploader("Upload file PDF", type="pdf")

    # extract the text
    if pdf is not None:
        st.header("Bước 2: Hỏi thông tin từ file PDF 💬")
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        # # Create vector DB
        # create_db_from_text(text)

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Mời bạn đặt câu hỏi:"):
            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            while True:
                response = query({
                    "inputs": {
                        "question": f"{prompt}",
                        "context": f"{text}"
                    },
                })
                # If session timeout, try again
                if 'answer' not in response:
                    st.write(f"{response}")
                    continue
                else:
                    # st.write(f"Câu trả lời mà chúng tôi tìm được: {response['answer']}")

                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        # response['answer'] = response['answer'].title()
                        st.write_stream(response_generator(response['answer']))
                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response['answer']})

                    break

        # # show user input
        # ''' Ví dụ:
        # Tổ chức Đoàn TNCS Hồ Chí Minh thành lập ngày nào?
        # '''
        # user_question = st.text_input("Mời bạn đặt câu hỏi:")
        # if user_question:
        #     while True:
        #         response = query({
        #             "inputs": {
        #                 "question": f"{user_question}",
        #                 "context": f"{text}"
        #             },
        #         })
        #         # If session timeout, try again
        #         if 'answer' not in response:
        #             st.write(
        #                 f"{response}")
        #             continue
        #         else:
        #             st.write(
        #                 f"Câu trả lời mà chúng tôi tìm được: {response['answer']}")
        #             break


if __name__ == "__main__":
    main()
