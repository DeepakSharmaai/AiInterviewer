import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
