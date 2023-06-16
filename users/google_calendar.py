from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, time, timedelta
from health.google_auth import get_credentials

def get_calendar_service():
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)
    return service

def get_events(calendar_id='primary', time_min=datetime.utcnow().isoformat() + 'Z', time_max=None):
    service = get_calendar_service()
    events_result = service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max,
                                          maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    return events

def create_event(summary, start_time, end_time, timezone='UTC', calendar_id='primary'):
    service = get_calendar_service()

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone,
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')
    return event