from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import pyttsx3

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = 'path/to/your/credentials.json' # Secure code best practices!

def get_upcoming_events(max_results=10):
    """Fetches upcoming events from the user's Google Calendar."""

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build('calendar', 'v3', credentials=credentials)

    now = datetime.now(datetime.timezone.utc).isoformat()  # Get current UTC time directly
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

def format_event(event):
    """Formats an event into a human-readable string."""
    start = event['start'].get('dateTime', event['start'].get('date'))
    start_time = datetime.datetime.fromisoformat(start).strftime("%I:%M %p")
    return f"{start_time}: {event['summary']}"

def read_schedule():
    """Reads upcoming events aloud using text-to-speech."""
    events = get_upcoming_events()

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speech rate can be adjusted as needed
   
    if not events:
        engine.say("You have no upcoming events today.")
    else:
        engine.say("Your schedule for today:")
        for event in events:
            engine.say(format_event(event))

    engine.runAndWait()

if __name__ == "__main__":
    read_schedule()
