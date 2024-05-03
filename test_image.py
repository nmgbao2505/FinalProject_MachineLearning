import streamlit as st
import time

# Main function
def main():
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")
    st.title("Waiting Time Indicator")

    # Slider to adjust waiting time
    wait_time = st.slider("Set Waiting Time (seconds):", min_value=1, max_value=10)
    with st.spinner("Waiting..."):
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
