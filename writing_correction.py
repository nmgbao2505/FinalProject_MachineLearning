import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain.chains import LLMChain
from transformers import pipeline
from happytransformer import HappyTextToText, TTSettings
gec = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
args = TTSettings(num_beams=5, min_length=1, max_length=1000)
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
translation = pipeline("translation", model="VietAI/envit5-translation", device=0, max_new_tokens=600)
template = """
What do you think about {topic} ?. Give me your honest opinionn and do not spread false information.
"""
prompt = PromptTemplate(template=template, input_variables=["topic"])
llm_chain = LLMChain(llm=llm, prompt=prompt)

def run():
    topic, grammar = st.tabs(['TẠO VĂN BẢN', 'SỬA NGỮ PHÁP'])
    with topic:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.write(message['text'])
        input_topic = st.chat_input("Nhập chủ đề của bạn vào đây")
        if input_topic:
            with st.chat_message("user"):
                st.markdown(input_topic)
            st.session_state.messages.append({"role": "user", "text": input_topic})

            response = llm_chain.run(input_topic)
            response = response.replace(prompt.format(topic=input_topic), "")
            response = translation("en: " + response)[0]["translation_text"]
            #Setting 'max_new_tokens" to 512 for translation pipeline

            with st.chat_message("assistant"):
                st.markdown(response[3:])
            st.session_state.messages.append({"role": "bot", "text": response})

    with grammar:
        text = st.text_area("Nhập văn bản cần sửa ngữ pháp vào đây")
        if st.button("Sửa ngữ pháp"):
            corrected_text = gec.generate_text("grammar: " + text, args=args)
            st.write(corrected_text.text)

if __name__ == "__main__":
    run()