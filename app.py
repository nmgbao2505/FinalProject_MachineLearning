import streamlit as st
from streamlit_option_menu import option_menu
import home
import chat_documents

# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
# Reference: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(
    page_title="Nhóm 8 - Webpage",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="auto",
)

# # Change background color of the sidebar
# st.markdown(
#     """
#     <style>
#     .st-emotion-cache-y2anb3 {
#         background-color: rgb(8 56 97);
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# Mapping from title to function
TITLE_TO_FUNCTION = {
    "Trang chủ": home.run,
    "Trò chuyện với dữ liệu": chat_documents.run,
}

# Mapping from title to icon
TITLE_TO_ICON = {
    "Trang chủ": "house-fill",
    "Trò chuyện với dữ liệu": "chat-square-text-fill",
    # "Tin nhắn": "💬",
}


class MultiApp:
    def __init__(self) -> None:
        pass

    def run() -> None:
        with st.sidebar:
            selected = option_menu(
                menu_title=None, menu_icon=None,
                options=[title for title in TITLE_TO_FUNCTION.keys()],
                default_index=0,
                icons=[icon for icon in TITLE_TO_ICON.values()],
                orientation="vertical",
                styles={
                    "container": {"padding": "1!important", "background-color": '#03172c'},
                    "icon": {"color": "#ffffff", "font-size": "20px"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#9ea8dc70",
                        "font-family": "\"Source Sans Pro\", sans-serif",
                    },
                    "nav-link-selected": {
                        "background-color": "#3c5af1",
                        "font-size": "18px",
                        "font-family": "\"Source Sans Pro\", sans-serif",
                        "font-weight": "bold",
                    },
                },
            )

        if selected in TITLE_TO_FUNCTION:
            TITLE_TO_FUNCTION[selected]()


def main() -> None:
    MultiApp.run()


if __name__ == "__main__":
    main()
