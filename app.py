import streamlit as st
import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai

# === Config / Secrets ===
openai.api_key = st.secrets["openai"]["api_key"]

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# === Google Calendar Integration ===
def get_upcoming_events():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_config({
            "installed": {
                "client_id": st.secrets["gcal"]["client_id"],
                "client_secret": st.secrets["gcal"]["client_secret"],
                "redirect_uris": [st.secrets["gcal"]["redirect_uri"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=5, singleEvents=True, orderBy='startTime').execute()

    return events_result.get('items', [])

# === Transcription using OpenAI Whisper ===
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

# === GPT-based Interview Evaluation ===
def evaluate_response(transcript):
    prompt = f"""
You are an AI interviewer. Evaluate the following candidate answer:

\"{transcript}\"

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

# === Streamlit UI ===
st.title("🎤 AI Interviewer")

st.subheader("📅 Upcoming Interviews (from Google Calendar):")
events = get_upcoming_events()
if not events:
    st.write("No upcoming events found.")
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        st.markdown(f"- **{event.get('summary', 'No Title')}** at {start}")

st.subheader("📁 Upload Audio File")
audio_file = st.file_uploader("Upload the interview recording (WAV/MP3)", type=["wav", "mp3"])

if audio_file is not None:
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.read())

    with st.spinner("Transcribing audio..."):
        transcript = transcribe_audio("temp_audio.wav")

    st.text_area("📝 Transcript:", transcript, height=200)

    with st.spinner("Evaluating interview..."):
        result = evaluate_response(transcript)

    st.subheader("📊 Evaluation Result")
    st.write(result)
