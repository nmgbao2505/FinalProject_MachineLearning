from transformers import pipeline
from langchain import PromptTemplate, LLMChain
from langchain import HuggingFaceHub

import requests
import os
import streamlit as st
from datasets import load_dataset
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast


def translate_article_Eng_Viet(article_hi):
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

    tokenizer.src_lang = "en_XX"
    encoded_hi = tokenizer(article_hi, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded_hi,
        forced_bos_token_id=tokenizer.lang_code_to_id["vi_VN"]
    )
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    
    translated_text_str = " ".join(translated_text)
    
    return translated_text_str


def generate_story(scenario,llm):
    template = '''
    CONTEXT: {scenario}
    STORY:
    '''
    prompt = PromptTemplate(template=template, input_variables=["scenario"])
    chain = LLMChain(prompt=prompt,llm=llm)
    story = chain.predict(scenario=scenario)
    return translate_article_Eng_Viet(story)


def img2text(url):
    image_to_text = pipeline('image-to-text', model="Salesforce/blip-image-captioning-base")
    
    text = image_to_text(url)[0]['generated_text']
    
    return text


def generate_story_from_scenario(scenario):
    repo_id = "tiiuae/falcon-7b-instruct"
    hf_token = "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"
    llm = HuggingFaceHub(huggingfacehub_api_token=hf_token, repo_id=repo_id, verbose=False, model_kwargs={"temperature": 0.1, "max_new_tokens": 1500})
    story = generate_story(scenario, llm)
    return story


def main():
    st.set_page_config(page_title='Image to text and audio')
    st.title("🔄 Chuyển ảnh thành văn bản")

    uploaded_file = st.file_uploader('🖼 Upload hình ảnh của bạn ở đây...')
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name, 'wb') as file:
            file.write(bytes_data)
        st.image(uploaded_file, caption='Ảnh đã tải lên. Đang xử lý ⌛ ', use_column_width=True)
        
        scenario = img2text(uploaded_file.name)
        
        engtovie = translate_article_Eng_Viet(scenario)
        
        story = generate_story_from_scenario(scenario)
        
        st.write('Đã xử lý xong ✅')
        st.write(engtovie)
        with st.expander('📖 Tiếng Anh'):
            st.write(scenario)
        with st.expander('💬 Câu chuyện có thể phát triển từ mô tả' ):
            st.write(story)

if __name__ == '__main__':
    main()