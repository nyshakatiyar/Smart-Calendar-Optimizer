import os
import pickle
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build  # <-- THIS WAS MISSING

# Google Calendar API settings
SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE = "Asia/Kolkata"  # Change to your timezone

class GoogleCalendarManager:
    def __init__(self):
        self.creds = None
        self.token_file = 'token.pickle'
        self.credentials_file = 'credentials.json'
        self.service = self.authenticate()

    def authenticate(self):
        """Handles OAuth 2.0 authentication"""
        # Load existing credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials, log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)

        return build('calendar', 'v3', credentials=self.creds)

    def add_events(self, events, time_slots, days_ahead=0):
        """Add events to Google Calendar"""
        base_date = datetime.now() + timedelta(days=days_ahead)
        results = []

        for event_name, time_slot in zip(events, time_slots):
            try:
                # Parse time slot (e.g., "2:00 PM")
                time_str, period = time_slot.split()
                hours, minutes = map(int, time_str.split(':'))
                
                if period.upper() == 'PM' and hours != 12:
                    hours += 12
                elif period.upper() == 'AM' and hours == 12:
                    hours = 0

                start_time = base_date.replace(hour=hours, minute=minutes)
                end_time = start_time + timedelta(hours=1)  # Default 1-hour duration

                event = {
                    'summary': event_name,
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': TIMEZONE,
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': TIMEZONE,
                    },
                }

                created_event = self.service.events().insert(
                    calendarId='primary',
                    body=event
                ).execute()

                results.append({
                    'status': 'success',
                    'event': event_name,
                    'time': time_slot,
                    'link': created_event.get('htmlLink')
                })

            except Exception as e:
                results.append({
                    'status': 'error',
                    'event': event_name,
                    'error': str(e)
                })

        return results