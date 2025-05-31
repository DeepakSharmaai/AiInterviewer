import openai
import streamlit as st

openai.api_key = st.secrets["openai"]["api_key"]

def evaluate_response(transcript):
    prompt = f"""
You are an AI interviewer. Evaluate the following candidate answer:

"{transcript}"

Give a score out of 10 on:
- Clarity
- Confidence
- Relevance

Then provide a brief feedback summary.
Respond in this format:
Clarity: #
Confidence: #
Relevance: #
Feedback: ...
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
