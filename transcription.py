import openai
import streamlit as st

openai.api_key = st.secrets["openai"]["api_key"]

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']
