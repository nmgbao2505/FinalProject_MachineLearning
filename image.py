from transformers import pipeline
from langchain import PromptTemplate, LLMChain
from langchain import HuggingFaceHub

import streamlit as st
from datasets import load_dataset
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image, ImageDraw

import re

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
    first_dash_index = story.find('-')
    processed_text = story[first_dash_index + 1:].strip()
    processed_text = re.sub(r'-', '', processed_text)
    sentences = processed_text.split('.')
    if 'Người dùng' in sentences[-1]:
        sentences = sentences[:-1]
    res = '.'.join(sentences)
    return res.strip()


def detect_objects_and_draw_bounding_boxes(url):
    image = Image.open(url)

    processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    draw = ImageDraw.Draw(image)
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        draw.rectangle(box, outline="green", width=2)
        draw.text((box[0], box[1]), f"{model.config.id2label[label.item()]} {round(score.item(), 3)}", fill="red")

    return image


def run():
    st.set_page_config(page_title='Image to text')
    st.title("🔄 Xử Lý Hình Ảnh và Tạo Câu Chuyện")

    uploaded_file = st.file_uploader('🖼 Upload hình ảnh của bạn ở đây...')
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name, 'wb') as file:
            file.write(bytes_data)
        st.image(uploaded_file, caption='Ảnh đã tải lên. Đang xử lý ⌛ ', use_column_width=True)
        
        scenario = img2text(uploaded_file.name)
        
        engtovie = translate_article_Eng_Viet(scenario)
        
        story = generate_story_from_scenario(scenario)
        
        processed_image = detect_objects_and_draw_bounding_boxes(uploaded_file.name)
        
        st.write('Đã xử lý xong ✅')
        st.write(f'Nội dung: {engtovie}')
        with st.expander('📖 Tiếng Anh'):
            st.write(scenario)
        with st.expander('💬 Câu chuyện có thể phát triển từ mô tả' ):
            st.write(story)
        
        with st.expander('🔎 Phát hiện các đối tượng trong ảnh' ):
            st.image(processed_image, caption='Ảnh với các đối tượng bên trong ảnh', use_column_width=True)


if __name__ == '__main__':
    run()