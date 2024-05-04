from dataclasses import dataclass
from typing import Literal, List
import streamlit as st
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
# from langchain_community.llms import HuggingFaceHub
from langchain_community.llms import HuggingFaceHub
from langchain.chains import LLMChain
from transformers import pipeline
from happytransformer import HappyTextToText, TTSettings
import streamlit.components.v1 as components

# **********************************************************
# * Phát update:
# *  - Dùng một hàm để khởi tạo các tham số cần thiết cho việc sửa ngữ pháp.
# **********************************************************
# gec = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
# args = TTSettings(num_beams=5, min_length=1, max_length=1000)

gec = None
args = None


def init_check_grammar_params():
    global gec, args

    gec = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
    args = TTSettings(num_beams=5, min_length=1, max_length=1000)


# **********************************************************
# * Phát update:
# *  - Dùng một hàm để khởi tạo các tham số cần thiết cho việc tạo văn bản.
# **********************************************************
llm = None
translation = None
template = None
prompt = None
llm_chain = None


def init_gen_text_params():
    global llm, translation, template, prompt, llm_chain

    llm = HuggingFaceHub(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        task="text-generation",
        model_kwargs={
            "max_new_tokens": 400,
            "top_k": 30,
            "temperature": 0.1,
            "repetition_penalty": 1.03,
        },
        huggingfacehub_api_token="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"
    )
    translation = pipeline(
        "translation",
        model="VietAI/envit5-translation",
        # device=0, # * Phát update: Comment tham số này để không báo lỗi
        max_new_tokens=600
    )
    template = """
    What do you think about {topic} ?. Give me your honest opinionn and do not spread false information.
    """
    prompt = PromptTemplate(template=template, input_variables=["topic"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)


# +--------------------------------------------------------+
# |                Dataclass for chat message               |
# +--------------------------------------------------------+
@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str


# +--------------------------------------------------------+
# |               Load CSS file for chat-form              |
# +--------------------------------------------------------+
def load_chat_form_css():
    with open("./static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


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

    # Init the text generation params
    init_gen_text_params()

    # Start the text generation process
    response = llm_chain.run(human_prompt)
    response = response.replace(prompt.format(topic=human_prompt), "")
    response = translation("en: " + response)[0]["translation_text"]
    response = response[3:].strip()
    # Setting 'max_new_tokens" to 512 for translation pipeline

    # Add the response to the history
    # Which means we have 2 more messages
    st.session_state.history.append(
        Message("human", human_prompt)
    )
    st.session_state.history.append(
        Message("ai", response)
    )


def run():
    # **********************************************************
    # * Phát update:
    # *  - Thêm tiêu đề cho chức năng.
    # *  - Chuyển tên chức năng sang kiểu chỉ viết hoa chữ cái đầu.
    # **********************************************************
    # topic, grammar = st.tabs(['TẠO VĂN BẢN', 'SỬA NGỮ PHÁP'])

    # Add the title to the function
    title = \
        f"""<p style="font-weight: bold; font-family: 'Poppins', sans-serif;
            font-size: 50px; border-radius: 2%;
            background-image: linear-gradient(43deg, #5a83f1 0%, #9e71c5 46%, #d2646f 100%);
            -webkit-background-clip: text; color: transparent;
            margin-left: 10px;">
                Tạo sinh văn bản và sửa lỗi ngữ pháp tiếng Anh
    </p>"""
    st.markdown(title, unsafe_allow_html=True)

    # Create 2 tabs for 2 functions
    topic, grammar = st.tabs(['Tạo văn bản', 'Sửa ngữ pháp'])

    with topic:
        # **********************************************************
        # * Phát update:
        # *  - Dùng CSS để tạo giao diện cho chức năng.
        # **********************************************************
        st.write("#")
        st.subheader("💭 Tạo văn bản từ chủ đề của bạn",
                     divider="violet")

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
            st.markdown("**Nhập chủ đề của bạn vào đây**")
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
            with st.spinner("Đang tạo văn bản..."):
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

    with grammar:
        # **********************************************************
        # * Phát update:
        # *  - Tạo `st.subheader()` để thể hiện mô tả.
        # *  - Ẩn label của `st.text_area()`.
        # *  - Thêm `st.spinner()` để hiển thị thông báo khi đang xử lý.
        # *  - Gọi hàm `init_check_grammar_params()` để khởi tạo tham số.
        # *  - Sử dụng `st.info()` để hiển thị kết quả.
        # **********************************************************
        st.write("#")
        st.subheader("✏️ Nhập văn bản mà bạn cần sửa ngữ pháp vào đây",
                     divider="violet")

        text = st.text_area("Nhập văn bản cần sửa ngữ pháp vào đây",
                            label_visibility="hidden")
        if st.button("Sửa ngữ pháp"):
            with st.spinner("Đang sửa ngữ pháp..."):
                # Init the grammar correction params
                init_check_grammar_params()

                # Call the grammar correction function
                corrected_text = gec.generate_text(
                    "grammar: " + text, args=args
                )

            # st.write(corrected_text.text)
            st.info(f"**Đoạn văn bản đúng ngữ pháp**: {corrected_text.text}")


if __name__ == "__main__":
    run()
