from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
import requests
import os
import streamlit as st
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf

HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')

def img2text(url):
    image_to_text = pipeline('image-to-text', model="Salesforce/blip-image-captioning-base")
    
    text = image_to_text(url)[0]['generated_text']
    
    return text

def text2speech(message):
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    inputs = processor(text=message, return_tensors="pt")
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

    sf.write("speech.wav", speech.numpy(), samplerate=16000)
        

def main():
    
    st.set_page_config(page_title='Image to text anhd audio')
    st.header('Turn img into text')
    uploaded_file = st.file_uploader('Choose an image...',type='jpg')
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name,'wb') as file:
            file.write(bytes_data)
        st.image(uploaded_file,caption='Uploaded Image.',use_column_width=True)
        scenario = img2text(uploaded_file.name)
        text2speech(scenario)
        
        
        st.write(scenario)
        st.audio('speech.wav')
        
        
        
        
if __name__ == '__main__':
    main()