import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar
from pytz import timezone

from .util import get_main_website, get_soup, la_timezone

from typing import List


utc_timezone = timezone("UTC")

url = "https://uwaterloo.ca/institute-for-quantum-computing/events"


def get_events() -> List[dict]:

    soup = get_soup(url)

    main_site_url = get_main_website(url)

    # Get all divs inside the div with the class "views-row"
    events = soup.find_all(class_="views-row")

    events_list = []

    # Loop through each event
    for ics_event in events:

        # Get the title of the event
        title_element = ics_event.find(class_="card__title")
        title = title_element.text
        title = title.strip()

        # Get the description of the event by using the href inside the title
        event_url = title_element.find("a")["href"]

        # Get the html for the event page
        event_page_html = requests.get(main_site_url + event_url).text
        event_page_soup = BeautifulSoup(event_page_html, "html.parser")

        # Get the calendar file of the event to extract the start and end times
        # (Other things are sometimes half-assed in their calendar files, and parsing the datetimes from their html is a pain)
        ics_element = event_page_soup.find(class_="view-interact")

        ics_url = ics_element.find("a")["href"]
        ics_text = requests.get(main_site_url + ics_url).text
        cal = Calendar.from_ical(ics_text)
        ics_event = cal.walk("vevent")[0]

        start_time = ics_event.get("dtstart").dt
        end_time = ics_event.get("dtend").dt

        start_time = start_time.astimezone(la_timezone)
        end_time = start_time.astimezone(la_timezone)

        # Ignore events that have already happened
        # NOTE: this would only miss events that have been added during the day and are taking place in the same day.
        #       (Assuming a 24-hour cycle of checking for new events)
        if start_time < datetime.now().astimezone(la_timezone):
            continue

        # Waterloo likes to add newlines and extra spaces to their descriptions for some reason
        title = event_page_soup.find(class_="page-title").text.strip()

        # Find the description element
        description_element = event_page_soup.find(class_="card__body")

        # Remove the email element from the description
        email_element = description_element.find(id="email-demo2")

        if email_element:
            email_element.decompose()

        description_raw_text = description_element.text

        # But sometimes they put the calendar thing in the description
        # This removes the part of the string starting with "Add event to calendar"

        # Get the index of the string "Add event to calendar"
        index = description_element.text.lower().find("add event to calendar")

        # If the string was found, remove the rest of the string
        if index != -1:
            description_raw_text = description_raw_text[:index]

        # Remove all the extra whitespace

        description = re.sub(r"\s+", " ", description_raw_text).strip()

        # Create the event json
        event_dict = {
            "summary": title,
            # "location": zoom_url,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "America/Los_Angeles",
            },
            "reminders": {"useDefault": True},
        }

        events_list.append(event_dict)

        print(f"Extracted event: {title}")

    return events_list
