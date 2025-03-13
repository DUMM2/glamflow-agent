import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarManager:
    def __init__(self):
        self.service = self._authenticate()

    ###########################################################################################################

    def _authenticate(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
                )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    ###########################################################################################################
        
    def list_upcomming_events(self, max_results=10):
        # Call the Calendar API
        now = datetime.datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
        _date = (datetime.datetime.now() + datetime.timedelta(days=3)).replace(hour=23, minute=59, second=0, microsecond=0).isoformat() + "Z"
        print("Getting the upcoming 10 events")
        events_result = (
            self.service.events().list(
                calendarId="primary",
                timeMin=now,
                timeMax=_date,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
        else:
            # Prints the start and name of the next 10 events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])

    ###########################################################################################################

    def create_event(self, summary, start_time, end_time, timezone, attendees=None):
        event = {
            'summary': summary,
            'start':
            {
                'dateTime':start_time,
                'timeZone':timezone,
            },
            'end':
            {
                'dateTime':end_time,
                'timeZone':timezone,
            }
        }

        if attendees:
            event["attendees"] = [{"email":email} for email in attendees]

        try:
            event = self.service.events().insert(calendarId="primary", body=event).execute()
            print(f"Evento creado: {event.get('htmlLink')}")
        except HttpError as error:
            print(f"Error :(: {error})")

calendar = GoogleCalendarManager()
#calendar.create_event("Pruebitas2", "2025-03-15T13:00:00-06:00", "2025-03-15T14:00:00-06:00", "America/Mexico_City", ["dan.uz.mont@gmail.com"])
calendar.list_upcomming_events()