import streamlit as st
from calendar import get_upcoming_events
from transcription import transcribe_audio
from interview_logic import evaluate_response

st.title("🎤 AI Interviewer")

st.markdown("Upload a recorded interview to evaluate the candidate.")

# Step 1: Show upcoming interviews
st.subheader("📅 Upcoming Interviews (from Google Calendar):")
events = get_upcoming_events()
for event in events:
    st.markdown(f"- **{event['summary']}** at {event['start']}")

# Step 2: Upload interview audio
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
