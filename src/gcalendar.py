import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from typing import List


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

calendar_id = json.load(open("jsons/settings.json", "r"))["calendarID"]


# Gets the credentials from the user's json files
def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("jsons/token.json"):
        creds = Credentials.from_authorized_user_file("jsons/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "jsons/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("jsons/token.json", "w") as token:
            token.write(creds.to_json())

    return creds


# Prints the list of calendars in the user's account
def print_calendars():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = get_creds()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        print("Getting list of calendars")
        calendars_result = service.calendarList().list().execute()

        calendars = calendars_result.get("items", [])

        if not calendars:
            print("No calendars found.")
        for calendar in calendars:
            summary = calendar["summary"]
            id = calendar["id"]
            print(f"{summary} ({id})")

    except HttpError as error:
        print(f"An error occurred: {error}")


def add_events(events: List[dict]):
    """Shows basic usage of the Google Calendar API.
    Adds the given event to the user's calendar.
    """

    creds = get_creds()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Get all the events in the calendar
        events_result = (
            service.events()
            .list(calendarId=calendar_id, singleEvents=True, orderBy="startTime")
            .execute()
        )

        # Get the ids of the events in the calendar
        # Summary is the title of the event
        event_titles = [event["summary"] for event in events_result.get("items", [])]

        # Call the Calendar API
        for event in events:
            if event["summary"] in event_titles:
                print(f"Event already exists: {event['summary']}")
                continue
            else:
                event = (
                    service.events()
                    .insert(calendarId=calendar_id, body=event)
                    .execute()
                )
                print(f"Event created: {(event.get('htmlLink'))}")

    except HttpError as error:
        print(f"An error occurred: {error}")


# Deletes all the events in the calendar
def purge_calendar():

    creds = get_creds()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Get all the events in the calendar
        events_result = (
            service.events()
            .list(calendarId=calendar_id, singleEvents=True, orderBy="startTime")
            .execute()
        )

        # Get the ids of the events in the calendar
        event_ids = [event["id"] for event in events_result.get("items", [])]

        # Call the Calendar API
        for event_id in event_ids:
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"Event deleted: {event_id}")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    add_events([])
