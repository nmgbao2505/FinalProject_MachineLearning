from dataclasses import dataclass
from typing import Literal
import streamlit as st
import requests
from PyPDF2 import PdfReader
import time
from typing import List, Dict
from streamlit.runtime.uploaded_file_manager import UploadedFile
from docx import Document
import streamlit.components.v1 as components

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


@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str

# ===================================================================


# +--------------------------------------------------------+
# |               Load CSS file for chat-form              |
# +--------------------------------------------------------+
def load_chat_form_css():
    with open("./static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


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
# |                Initialize session state                |
# +--------------------------------------------------------+
def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []


# +--------------------------------------------------------+
# |                   Callback function                    |
# +--------------------------------------------------------+
def on_click_callback():
    # Get the human prompt
    human_prompt = str(st.session_state.human_prompt).strip()

    # If the human prompt is empty, return
    if not human_prompt:
        return

    # Generate the response
    response = "\n\n"
    for result in generate_single_answer(human_prompt):
        response += generate_response_structure(result) + "\n\n"

    # Add the response to the history
    # Which means we have 2 more messages
    st.session_state.history.append(
        Message("human", human_prompt)
    )
    st.session_state.history.append(
        Message("ai", response)
    )


# +--------------------------------------------------------+
# |                        Main call                       |
# +--------------------------------------------------------+
def run() -> None:
    print("_"*100)
    print("Main call")

    # Set the title
    render_title("Trò chuyện với tài liệu của bạn")

    # Step 1: Upload file PDF
    st.write("#")
    st.header("📚 Đăng tải tài liệu của bạn ở đây", divider="violet")
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
        st.header("💬 Hỏi thông tin từ tài liệu", divider="violet")

        # Set up the chat form
        load_chat_form_css()
        initialize_session_state()

        # Generate the chat form
        chat_placeholder = st.container()
        prompt_placeholder = st.form("chat-form")
        credit_card_placeholder = st.empty()

        # +--------------------------------------------------------+
        # |                    Render chat form                    |
        # +--------------------------------------------------------+

        def render_chat_form(history: List[Message]) -> None:
            """ Render the chat form

            Args:
                history (List[Message]): List of chat messages
            """

            with chat_placeholder:
                for chat in history:
                    div = f"""
            <div class="chat-row {'' if chat.origin == 'ai' else 'row-reverse'}">
                <img class="chat-icon" src="app/static/{'ai_icon.png' if chat.origin == 'ai' else 'user_icon.png'}" width=32 height=32>
                <div class="chat-bubble {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
                    &#8203;{chat.message}</div></div>
                    """
                    st.markdown(div, unsafe_allow_html=True)

                for _ in range(3):
                    st.markdown("")

        # Render all chat messages when starting
        render_chat_form(st.session_state.history)

        # Render the chat form
        with prompt_placeholder:
            st.markdown("**Nhập câu hỏi của bạn**")
            cols = st.columns((6, 1))
            cols[0].text_input(
                "Chat",
                value=" ",
                label_visibility="collapsed",
                key="human_prompt",
            )
            is_submitted = cols[1].form_submit_button(
                "Gửi",
                type="primary",
                # on_click=on_click_callback,
            )

        # If the form is submitted
        if is_submitted:
            # Generate the response
            with st.spinner("Đang tìm kiếm câu trả lời..."):
                on_click_callback()

            # Render the newest chat history
            # (2 messages from both user and AI)
            if len(st.session_state.history) % 2 != 0:
                raise ValueError("The number of messages should be even")

            render_chat_form(st.session_state.history[-2:])

        components.html("""
        <script>
        const streamlitDoc = window.parent.document;

        const buttons = Array.from(
            streamlitDoc.querySelectorAll('.stButton > button')
        );
        const submitButton = buttons.find(
            el => el.innerText === 'Submit'
        );

        streamlitDoc.addEventListener('keydown', function(e) {
            switch (e.key) {
                case 'Enter':
                    submitButton.click();
                    break;
            }
        });
        </script>
        """, height=0, width=0,)


if __name__ == "__main__":
    run()
