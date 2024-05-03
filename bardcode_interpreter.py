"""
Details : AutoBard-Coder is code genrator for bard. It is used to generate code from bard response.
its using Bard API to interact with bard and refine the results for coding purpose.
The main purpose of this is for research and educational purpose.
This is using official PALM API to generate code now.
This can generate the code from prompt and fix itself unless the code is fixed.
Language : Python
Dependencies : streamlit, bard-coder
Author : HeavenHM.
License : MIT
Date : 21-05-2023
Updated Date : 28-09-2023
"""

# Import the required libraries
import logging
import streamlit as st
import time
import traceback
from libs.bardcoder_lib import BardCoder
from libs.logger import logger
from io import StringIO
from libs.sharegpt_api import sharegpt_get_url
from libs.blacklist_commands import harmful_commands_python, harmful_commands_cpp, harmful_prompts
from PIL import Image
import tokenize
from stat import S_IREAD, S_IRGRP, S_IROTH
import re
import io
import os
from os import path
from streamlit_extras.stylable_container import stylable_container

BARD_FILE_SIZE_LIMIT = 10000


def init_session_state():
    if "bard_coder" not in st.session_state:
        st.session_state.bard_coder = None

    if "api_key_initialized" not in st.session_state:
        st.session_state.api_key_initialized = False

    if "code_output" not in st.session_state:
        st.session_state.code_output = ""

    if "messages" not in st.session_state:
        st.session_state.messages = ""

    if "text_area" not in st.session_state:
        st.session_state.text_area = ""

    if "file_size" not in st.session_state:
        st.session_state.file_size = 0

    if "file_char_count" not in st.session_state:
        st.session_state.file_char_count = 0


def init_bard_coder_session(api_key=None, temperature=0.1, max_output_tokens=2048, mode='precise'):
    try:
        bard_coder = BardCoder(api_key=api_key, model="text-bison-001", temperature=temperature,
                               max_output_tokens=max_output_tokens, mode=mode, guidelines=["exception_handling", "error_handling", "code_only"])
    except Exception as e:
        logger.error(f"Error initializing BardCoder session: {e}")
        raise
    return bard_coder


def make_code_interpreter_read_only(files=[], folders: str = "libs"):
    for filename in files:
        logger.info(f"Making {filename} read-only")
        os.chmod(filename, S_IREAD | S_IRGRP | S_IROTH)

    logger.info(f"Making all files in {folders} folder read-only")
    folder = folders
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        os.chmod(filepath, S_IREAD | S_IRGRP | S_IROTH)


def create_dirs_on_startup():
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("codes"):
        os.makedirs("codes")


def auto_bard_execute(prompt, code_file='code.txt', code_choices='code_choice', expected_output=None, exec_type='single', rate_limiter_delay=5):
    try:
        code = st.session_state.bard_coder.generate_code(prompt, 'python')

        # print the code in output.
        if code:
            # **********************************************************
            # * Phát update:
            # *  - Chỉnh CSS để code tạo ra không bị trùng với màu nền.
            # **********************************************************
            # Override Streamlit's default CSS for code blocks
            st.markdown(
                """
                <style>
                pre {
                    background: rgb(240, 242, 246) !important;
                }
                .st-emotion-cache-eqsky5 {
                    color: #03172C !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.code(code, language='python')

        # Save the code to file
        if st.session_state.save_file and code and len(code) > 0:
            logger.info("Saving generated code to file")
            saved_file = st.session_state.bard_coder.save_code(code_file)

        return saved_file, False

    except Exception as exception:
        stack_trace = traceback.format_exc()
        st.info(str(exception))
        logger.error(
            f"Exception {exception} occurred while executing the code {stack_trace}")


def auto_bard_setup(prompt, code_file='code.txt', code_choices='code_choice', expected_output=None, exec_type='single', rate_limiter_delay=5):

    code_file = path.join("codes", code_file)
    test_cases_output = 0

    saved_file, status = auto_bard_execute(
        prompt, code_file, code_choices, expected_output, exec_type)
    code_output = None

    if ~status:
        if code_output and code_output != None and code_output.__len__() > 0:

            if code_output is not None:
                code_output = "".join(code_output)
            else:
                code_output = ""

            if code_output:
                while 'error' in code_output.lower() or 'exception' in code_output.lower():
                    logger.info(
                        "Error in executing code, trying to fix the code with error")
                    st.info(
                        "Error in executing code,Trying to fix the code with error")

                    code = st.session_state.bard_coder.get_code()
                    prompt = f"I got error while running the code {code_output}.\nPlease fix the code ``\n`{code}\n``` \nand try again.\nHere is error {code_output}\n\n" + \
                        "Note:The output should only be fixed code and nothing else. No explanation or anything else."

                    logger.info("Starting bard coder process again")
                    code_output, saved_file, status = auto_bard_execute(
                        prompt, code_file, code_choices, expected_output, exec_type)
                    time.sleep(rate_limiter_delay)
                    test_cases_output += 1

            st.code(code_output, language="python")

            if code_output and expected_output and code_output.__len__() > 0:

                while expected_output not in code_output:
                    logger.info(
                        f"Expected output {expected_output} not found in code\nOutput: {code_output}")
                    st.info(
                        f"Expected output {expected_output} not found in code\nOutput: {code_output}")

                    code = st.session_state.bard_coder.get_code()
                    prompt = f"I got output {code_output}.\nPlease fix the code ``\n`{code}\n```  \nand try again.\nHere is expected output: {code_output}\n\n" + \
                        "Note:The output should only be fixed code and nothing else. No explanation or anything else."

                    logger.info("Starting bard coder process again")
                    code_output, saved_file, status = auto_bard_execute(
                        prompt, code_file, code_choices, expected_output, exec_type)

                    logger.info("Sleeping for rate limiter delay")
                    time.sleep(rate_limiter_delay)
                    test_cases_output += 1

                logger.info("Code has been fixed for expected output")
                st.info("Code has been fixed for expected output")
                st.info(code_output)

    return code_output, saved_file, status


def is_prompt_safe(prompt):
    logger.info("Starting is_prompt_safe method")
    if prompt is None:
        logger.info("Prompt is Empty")
        return False

    logger.info("Checking prompt for safety")

    prompt_list = [re.sub(r'[^\w\s]', '', re.sub(r'(\*\*|__)(.*?)(\*\*|__)', r'\2', re.sub(
        r'^\W+|\W+$', '', item))).strip() for item in re.split('\n| ', prompt.lower()) if item.strip() != '']
    prompt_list = [re.sub(r'\d+', '', i) for i in prompt_list]
    logger.info(f"Prompt list is {prompt_list}")

    for command in harmful_prompts:
        if command in prompt_list:
            logger.info(
                f"Prompt is not safe because of illegal command found '{command}'")
            return False, command
    logger.info(f"Input Prompt is safe")
    return True, None


def tokenize_source_code(source_code):
    logger.info("Starting tokenize_source_code method")
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source_code).readline):
            if token.type not in [tokenize.ENCODING, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT]:
                if any(char in token.string for char in ['::', '.', '->', '_']) or token.string.isalnum():
                    token_str = re.sub(r'\'|\"', '', token.string)
                    tokens.append(token_str)
    except tokenize.TokenError:
        if st.session_state.bard_coder:
            logger.error("Error parsing the tokens")
    if tokens:
        tokens = list(([token.lower() for token in tokens]))
    if st.session_state.bard_coder:
        logger.info(
            f"Tokenise was called and Tokens length is {tokens.__len__()}")
    return tokens


def is_code_safe(code):
    logger.info("Starting is_code_safe method")
    if st.session_state.bard_coder:
        logger.info("Checking code for safety")

    harmful_code_commands = harmful_commands_python + harmful_commands_cpp

    tokens_list = tokenize_source_code(code)

    output_dict = []

    for command in harmful_code_commands:
        for token in tokens_list:
            if command == token:
                output_dict.append((False, command, token))

    if output_dict is None or output_dict.__len__() == 0:
        output_dict = [(True, None, None)]
    if st.session_state.bard_coder:
        logger.info(f"Output dict is {output_dict}")
    return output_dict


def dsiplay_buttons(is_prompt_valid: bool):
    col1, _, _ = st.columns(3, gap='large')

    with col1:
        run_button = st.button("Tạo code", key="run-button", use_container_width=True,
                               disabled=not is_prompt_valid)

    return run_button


def run():
    # **********************************************************
    # * Phát update:
    # *  - Thêm tiêu đề cho chức năng.
    # **********************************************************

    # Add the title to the function
    title = \
        f"""<p style="font-weight: bold; font-family: 'Poppins', sans-serif;
            font-size: 50px; border-radius: 2%;
            background-image: linear-gradient(43deg, #5a83f1 0%, #9e71c5 46%, #d2646f 100%);
            -webkit-background-clip: text; color: transparent;
            margin-left: 10px;">
                Trình tạo mã nguồn theo yêu cầu
    </p>"""
    st.markdown(title, unsafe_allow_html=True)

    try:
        create_dirs_on_startup()

        file = __file__
        filenames = [file, file.replace("bardcode_interpreter", "bardcoder")]

        upload_prompt_data, upload_data, uploaded_file = None, None, None

        init_session_state()

        try:
            # **********************************************************
            # * Phát update:
            # *  - Tạo `st.subheader()` để thể hiện mô tả.
            # *  - Thêm `st.info()` để thông báo tên file sẽ được lưu.
            # **********************************************************
            st.write("#")
            st.subheader("🔗 Nhập tên file mà bạn muốn lưu", divider="violet")

            code_file = st.text_input("Nhập tên file muốn lưu:", value="",
                                      label_visibility="hidden",)
            st.session_state.safe_system = True
            st.session_state.save_file = True
            if code_file:
                st.info(f"**Mã nguồn sẽ được lưu vào file**: {code_file}",
                        icon="📁")

            # **********************************************************
            # * Phát update:
            # *  - Tạo `st.subheader()` để thể hiện mô tả.
            # **********************************************************
            st.write("#")
            st.subheader("📚 Đăng tải file dữ liệu của bạn ở đây",
                         divider="violet")

            uploaded_file = st.file_uploader("Chọn file",
                                             label_visibility="hidden",)
            if uploaded_file is not None:

                # To read file as bytes:
                bytes_data = uploaded_file.getvalue()
                # get the file size
                st.session_state.file_size = uploaded_file.size

                # To convert to a string based IO:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                # To read file as string:
                upload_data = stringio.read()

                # Count the number of characters in the file
                st.session_state.file_char_count = len(upload_data)

                # write the file to uploads directory
                with open(uploaded_file.name, "w") as f:
                    f.write(upload_data)

                # Display a success message
                st.success("Tải file lên thành công")
        except Exception as exception:
            logger.info(f"Lỗi {exception}")

        # **********************************************************
        # * Phát update:
        # *  - Tạo `st.subheader()` để thể hiện mô tả.
        # **********************************************************
        st.write("#")
        st.subheader("👨‍💻 Nhập yêu cầu của bạn ở đây",
                     divider="violet")

        # Use the text_area variable from the session state for input
        prompt = st.text_area(placeholder="Nhập yêu cầu của bạn", label="Prompt",
                              label_visibility="hidden", height=300, key="text_area_input")

        # check if prompt is changed.
        if prompt != st.session_state.text_area:
            logger.info(
                f"Prompt changed from '{st.session_state.text_area}' to '{prompt}'")
            st.session_state.text_area = prompt

        character_count: int = len(st.session_state.text_area)

        # Status info message. (Char count and file size)
        status_info_msg = f"Số lượng kí tự:{character_count}/{BARD_FILE_SIZE_LIMIT}"

        if st.session_state.file_size > 0:
            logger.info(
                f"File Char count is {st.session_state.file_char_count}")
            character_count += st.session_state.file_char_count
            # Update the character count for file size.
            status_info_msg = f"Số lượng kí tự: {character_count}/{BARD_FILE_SIZE_LIMIT}"
            status_info_msg += " | " + \
                f"Kích thước của file là {st.session_state.file_size/1024:.2f}Kb | {st.session_state.file_size/1024/1024:.2f}Mb"

        st.info(status_info_msg)

        # check the Prompt for safety and file size exceeding 4,000 characters.
        prompt_safe = True
        if st.session_state.bard_coder and st.session_state.safe_system:
            prompt_safe, command = is_prompt_safe(prompt)
            if not prompt_safe:
                logger.info(
                    f"Error in prompt because of unsafe command found '{command}'")
                st.error(
                    f"Error in prompt because of illegal command found '{command}'")

        if character_count > BARD_FILE_SIZE_LIMIT or st.session_state.file_char_count > BARD_FILE_SIZE_LIMIT:
            st.error(
                f"Error in prompt The file size limit exceeded {BARD_FILE_SIZE_LIMIT} characters")

        palm_api_key = "AIzaSyAwsPd5aFAKijvFanRIbEnkh6EwlFQdLcY"

        if palm_api_key and not st.session_state.api_key_initialized:
            st.session_state.bard_coder = init_bard_coder_session(
                palm_api_key, 0.1, 2048, "precise")

        # Setting the buttons for the application
        run_button = dsiplay_buttons(
            prompt_safe and st.session_state.file_char_count < BARD_FILE_SIZE_LIMIT)

        # Setting application to run
        if run_button:
            with st.spinner('Đang xử lý ⌛'):
                saved_file = None

                # Append the uploaded file data to prompt
                if upload_data:
                    prompt += "\n" + f"Here is the file called {uploaded_file.name} at location {uploaded_file.name} data.\n" + \
                        f"```\n{upload_data}\n```"

                # If graph were requested.
                if 'graph' in prompt.lower():
                    prompt += "\n" + "using Python use Matplotlib save the graph in file called 'graph.png'"

                # if Chart were requested
                if 'chart' in prompt.lower() or 'plot' in prompt.lower():
                    prompt += "\n" + "using Python use Plotly save the chart in file called 'chart.png'"

                # if Table were requested
                if 'table' in prompt.lower():
                    prompt += "\n" + "using Python use Pandas save the table in file called 'table.md'"

                # Refine the prompt for harmful commands.
                try:
                    if prompt_safe:
                        # Run the auto bard setup process.
                        log_container = st.empty()
                        st.session_state.code_output, saved_file, status = auto_bard_setup(
                            prompt, code_file)
                        if st.session_state.code_output:
                            st.code(st.session_state.code_output,
                                    language='python')
                            pass
                    else:
                        st.error(
                            f"Cannot execute the prompt because of illegal command found '{command}'")
                        logger.info(
                            f"Cannot execute the prompt: '{prompt}' because of illegal command found '{command}'")
                        st.stop()
                except Exception as exception:
                    logger.info(f"Error in auto bard setup {exception}")

    except Exception as exception:
        # show_outputf the stack trace
        stack_trace = traceback.format_exc()
        st.error("Error: " + str(exception))
        logger.error(f"Error: {exception}\n{stack_trace}")


if __name__ == "__main__":
    run()
