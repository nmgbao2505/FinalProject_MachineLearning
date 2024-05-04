import streamlit as st
import requests
from PyPDF2 import PdfReader
import time
from typing import List, Dict
from streamlit.runtime.uploaded_file_manager import UploadedFile
from docx import Document

# # Model đã thử nghiệm:
# #   - VietAI/vit5-base => Không tốt
# #   - VietAI/vit5-large => Load không nổi
# #   - timpal0l/mdeberta-v3-base-squad2 => Kết quả tiếng Việt không tốt
# # model_checkpoint = "nguyenvulebinh/vi-mrc-base"
# # model_checkpoint = "nguyenvulebinh/vi-mrc-large"

# model_checkpoint = "ancs21/xlm-roberta-large-vi-qa"

# ========================== CONFIGURATION ==========================

# Reference: https://huggingface.co/ancs21/xlm-roberta-large-vi-qa
API_URL = "https://api-inference.huggingface.co/models/ancs21/xlm-roberta-large-vi-qa"
headers = {"Authorization": "Bearer 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"}
DOCUMENTS: Dict[str, List[Dict]] = {}
MIN_SCORE = 0.0  # Min score to accept the answer

# ===================================================================


# +--------------------------------------------------------+
# |        Call API to get the answer from the model       |
# +--------------------------------------------------------+
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


# +--------------------------------------------------------+
# | Utility functions to read different types of documents |
# +--------------------------------------------------------+
def read_md_document(uploaded_md_file: UploadedFile) -> None:
    # Current document
    document = []

    # Get the content of the uploaded file
    md_lines = uploaded_md_file.getvalue().decode('utf-8')
    md_lines = md_lines.split("\n")

    # Extract neccessary information
    for i, line in enumerate(md_lines):
        content = line.strip("\r# ")
        if not content:  # Skip empty line
            continue
        document.append({
            'content': content,
            'paragraph_number': i+1
        })

    # Update the global DOCUMENTS
    DOCUMENTS[uploaded_md_file.name] = document


def read_txt_document(uploaded_txt_file: UploadedFile) -> None:
    # Current document
    document = []

    # Get the content of the uploaded file
    doc_lines = uploaded_txt_file.getvalue().decode('utf-8')
    doc_lines = doc_lines.split("\n")

    # Extract neccessary information
    for i, line in enumerate(doc_lines):
        content = line.strip("\r ")
        if not content:  # Skip empty line
            continue
        document.append({
            'content': content,
            'paragraph_number': i+1
        })

    # Update the global DOCUMENTS
    DOCUMENTS[uploaded_txt_file.name] = document


def read_docx_document(uploaded_docx_file: UploadedFile) -> None:
    # Current document
    document = []

    # Load the docx document
    doc_file = Document(uploaded_docx_file)

    # Extract neccessary information
    for i, paragraph in enumerate(doc_file.paragraphs):
        document.append({
            'content': paragraph.text.strip(),
            'paragraph_number': i+1
        })

    # Update the global DOCUMENTS
    DOCUMENTS[uploaded_docx_file.name] = document


def read_pdf_document(uploaded_pdf_file: UploadedFile) -> None:
    # Current document
    document = []

    # Create a PDF file reader
    pdf_reader = PdfReader(uploaded_pdf_file)

    # Extract content and page number from PDF file
    for page_idx, page in enumerate(pdf_reader.pages):
        # Append to the current document
        document.append({
            'content': page.extract_text().strip(),
            'page_number': page_idx + 1,
        })

    # Update the global DOCUMENTS
    DOCUMENTS[uploaded_pdf_file.name] = document


# +--------------------------------------------------------+
# |          Generate answer for a single question         |
# +--------------------------------------------------------+
def generate_single_answer(question: str) -> List[Dict]:
    # List of answers
    answers = []

    for file_name, doc_contexts in DOCUMENTS.items():
        context = ""        # Context of the document
        end_char_idx = [0]  # End character index of each page/paragraph

        # Get full context of the document
        for doc_context in doc_contexts:
            end_char_idx.append(end_char_idx[-1]+len(doc_context['content']))
            context += doc_context['content'] + " "

        context.rstrip()    # Remove white spaces

        # Try to get the answer from the model
        for i in range(1, 101):
            result = query({
                "inputs": {
                    "question": question,
                    "context": context
                },
            })

            # print(f"{i},", end="")

            # If we have the answer, break
            if 'answer' in result:
                result['answer'] = result['answer'].strip()
                print(result)
                break

        # If the score is too low, skip
        if result['score'] < MIN_SCORE:
            continue

        # Add the file name
        result['file_name'] = file_name

        # Get the page/paragraph number
        for i in range(len(end_char_idx[1:])):
            if result['end'] <= end_char_idx[i+1]:
                if file_name.endswith('.pdf'):
                    result['page_number'] = i+1
                else:
                    result['paragraph_number'] = i+1
                break

        # Update the answer
        answers.append(result)

    # Sort the answers by score
    answers = sorted(answers, key=lambda x: x['score'], reverse=True)

    return answers


# +--------------------------------------------------------+
# |         Generate response structure for display        |
# +--------------------------------------------------------+
def generate_response_structure(result: Dict) -> str:
    response = ""

    # Document's name
    response += f"**Từ tài liệu**: {result['file_name']}"

    # Page/Paragraph number
    if 'page_number' in result:
        response += "  \n" + f"**Trang**: {result['page_number']}"
    elif 'paragraph_number' in result:
        response += "  \n" + f"**Đoạn**: {result['paragraph_number']}"

    # Answer
    response += "  \n" + f"**Câu trả lời**: {result['answer'].strip()}"

    return response


# +--------------------------------------------------------+
# |             Response generator for display             |
# +--------------------------------------------------------+
def response_generator(response: str):
    for word in response.split(sep=" "):
        yield word + " "
        time.sleep(0.05)


# +--------------------------------------------------------+
# |                  Render function title                 |
# +--------------------------------------------------------+
def render_title(title: str) -> None:
    title = \
        f"""<p style="font-weight: bold; font-family: 'Poppins', sans-serif;
                font-size: 50px; border-radius: 2%;
                background-image: linear-gradient(43deg, #5a83f1 0%, #9e71c5 46%, #d2646f 100%);
                -webkit-background-clip: text; color: transparent;
                margin-left: 10px;">
                    {title}
        </p>"""
    st.markdown(title, unsafe_allow_html=True)


# +--------------------------------------------------------+
# |                        Main call                       |
# +--------------------------------------------------------+
def run() -> None:
    print("_"*100)
    print("Main call")

    # Set the title
    render_title("Trò chuyện với dữ liệu của bạn")

    # Step 1: Upload file PDF
    st.write("#")
    st.header("📚 Đăng tải dữ liệu của bạn ở đây", divider="violet")
    uploaded_files = st.file_uploader(
        label=" ",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )

    # Extract the text if uploaded files are found
    if uploaded_files:
        print(">> Found uploaded files")
        for uploaded_file in uploaded_files:
            # If file has been read, skip
            if uploaded_file.name in DOCUMENTS:
                continue

            if uploaded_file.type.endswith("pdf"):
                read_pdf_document(uploaded_file)
            elif uploaded_file.name.endswith("docx"):
                read_docx_document(uploaded_file)
            elif uploaded_file.type.endswith('text/plain'):
                read_txt_document(uploaded_file)
            elif uploaded_file.name.endswith('md'):
                read_md_document(uploaded_file)

        print(">> Finish reading documents")

        # Step 2: Ask questions
        st.write("#")
        st.header("💬 Hỏi thông tin từ dữ liệu", divider="violet")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Xin chào, tôi là Pratt. Hãy đặt câu hỏi để tôi trả lời cho bạn."
            }]

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if question := st.chat_input(placeholder="Mời bạn đặt câu hỏi:"):
            question = question.strip()
            print(">> Question:", question)

            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": question}
            )

            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(question)

            # Get the answer
            response = ""
            with st.spinner("Đang xử lý..."):
                for result in generate_single_answer(question):
                    response += generate_response_structure(
                        result) + "  \n" * 2

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.write_stream(response_generator(response))

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )


if __name__ == "__main__":
    run()
