import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def run() -> None:

    # +--------------------------------------------------------+
    # |                     USE LOCAL CSS                      |
    # +--------------------------------------------------------+
    def local_css(file_name: str):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("style/style.css")

    # +--------------------------------------------------------+
    # |                       LOAD ASSETS                      |
    # +--------------------------------------------------------+
    lottie_assistant = load_lottieurl(
        "https://lottie.host/0a3b4c6b-8099-4111-ada9-2fa028b8c9b4/vZz8lO7Jp3.json"
    )

    # +--------------------------------------------------------+
    # |                     HEADER SECTION                     |
    # +--------------------------------------------------------+
    with st.container():
        st.subheader(":wave: Xin chào, tôi là Pratt")
        st.title("Một trợ lý ảo hỗ trợ bạn trong học tập và công việc hàng ngày")

    # +--------------------------------------------------------+
    # |                        WHAT I DO                       |
    # +--------------------------------------------------------+
    with st.container():
        # Render a horizontal line
        st.write("---")
        left_column, right_column = st.columns(2)

        # For left column
        with left_column:
            st.header("⚙️ Tôi có thể giúp gì cho bạn?")
            st.write("##")
            st.write(
                """
                Trên trang web này, tôi cung cấp một số chức năng hữu ích giúp cho việc học
                và làm việc của bạn trở nên dễ dàng hơn. Dưới đây là một số chức năng mà bạn có thể
                sử dụng:
                
                - 💬 **Trò chuyện với dữ liệu**: Sau khi bạn đăng tải dữ liệu lên trang web, tôi sẽ 
                giúp bạn trả lời các câu hỏi bằng cách tra cứu thông tin từ tài liệu đó.
                

                Nếu các tính năng trên có xuất hiện lỗi hoặc nếu bạn có bất kỳ yêu cầu nào khác, đừng ngừng ngại
                liên hệ với tôi qua email.
                """
            )
        with right_column:
            st_lottie(
                animation_source=lottie_assistant,
                speed=1,
                reverse=False,
                loop=True,
                quality="low",  # medium ; high
                height=300, width=300,
                key="assistant",
            )

    # +--------------------------------------------------------+
    # |                         CONTACT                        |
    # +--------------------------------------------------------+
    with st.container():
        st.write("---")
        st.header("📬 Hãy liên lạc với tôi qua email!")
        st.write("##")

        # Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
        contact_form = """
        <form action="https://formsubmit.co/pvminh0309@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Tên của bạn" required>
            <input type="email" name="email" placeholder="Email của bạn" required>
            <textarea name="message" placeholder="Tin nhắn của bạn" required></textarea>
            <button type="submit">Gửi</button>
        </form>
        """

        left_column, right_column = st.columns(2)
        with left_column:
            st.markdown(contact_form, unsafe_allow_html=True)
        with right_column:
            st.empty()


if __name__ == "__main__":
    run()
