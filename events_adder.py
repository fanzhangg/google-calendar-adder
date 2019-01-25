"""
Create calendar events & add them to your user's calendar
Reference: https://developers.google.com/calendar/create-events
"""

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from table_parser import TableParser
import re


def get_service():
    """
    Get the service of Google Calendar
    :return: service
    """
    # add an event
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    # delete the credential if existed
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    # let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_events(url: str, table_head: str)->list:
    """
    Get the events from the table
    :return: events
    """
    parser = TableParser(url, table_head)
    return parser.extract_table()


def get_start(date: str) -> str:
    """reformat date retrieved from the table
    :param date: the date string retrieved from the table ("January 15")
    :return: the string of date which matches event.insert()'s format
    """
    months = {'January': '1',
              'February': '2',
              'March': '3',
              'April': '4',
              'May': '5',
              'June': '6',
              'July': '7',
              'August': '8',
              'September': '9',
              'December': '10',
              'November': '11'}
    # get the first month ('January')
    month = months.get(re.findall('[A-Z][a-z]+', date)[0])
    # get the first day ('13')
    day = re.findall('[1-9]+', date)[0]
    return f'2019-{month}-{day}'


def get_end(date: str) -> str:
    months = {'January': '1',
              'February': '2',
              'March': '3',
              'April': '4',
              'May': '5',
              'June': '6',
              'July': '7',
              'August': '8',
              'September': '9',
              'December': '10',
              'November': '11'}

    # get the last month, does not exclude the condition with only one month
    month = months.get(re.findall('[A-Z][a-z]+', date)[-1])
    # get the last day
    day = re.findall('[0-9]+', date)[-1]
    return f'2019-{month}-{day}'


def add_events(events, service):
    """
    Add the events to google calendar
    :param events: the events extracted from the table
    :param service: the service of Google calendar
    """
    for event in events:
        date = event.get('date')
        start = get_start(date)
        end = get_start(date)
        print('date:', date)
        print('start', start)
        print('end', end)
        summary = event.get('summary')
        calendar_event = {
            'summary': f'{summary}',
            'location': '1600 Grand Avenue, St Paul, MN55105',
            'description': '',
            'start': {
                # date, in the format "yyyy-mm-dd", if this is an all-day event
                'date': f'{start}',
                'timeZone': 'America/Chicago',
            },
            'end': {
                # date, in the format "yyyy-mm-dd", if this is an all-day event
                'date': f'{end}',
                'timeZone': 'America/Chicago',
            },
            # recurrence: specify recurrence information in calendar components
            # ref: https://tools.ietf.org/html/rfc5545#section-3.8.5
            'recurrence': [
                # RRULE(recurrence rule): defines arule or repeating pattern for recurring events, to-dos, journal
                # entries, or time zone definitions

                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'reminders': {
                'useDefault': False,
                "overrides": [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        calendar_event = service.events().insert(calendarId='primary', body=calendar_event).execute()
        print(f'Event created {event}')


if __name__ == "__main__":
    url = input('url:')
    head = input('head')
    events = get_events(url, head)
    service = get_service()
    add_events(events, service)


