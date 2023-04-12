from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from typing import List

from .util import get_main_website, get_soup, la_timezone


url = "https://simons.berkeley.edu/programs-events/public-lectures#nav-upcoming"

zoom_url = "https://berkeley.zoom.us/j/95040632440"


def get_events() -> List[dict]:
    soup = get_soup(url)

    main_site_url = get_main_website(url)

    # Get all divs inside the div with the class "views-row"
    events = soup.find_all(class_="views-row")

    events_list = []

    # Loop through each event
    for event in events:
        ## Get the time of the event in all elements with the class "time"
        time_elements = event.find_all(class_="datetime")

        # Get the starting and ending time in string format
        starting_datetime_str = time_elements[0]["datetime"]
        ending_datetime_str = time_elements[1]["datetime"]

        # Convert the string to a datetime object
        start_time = parser.parse(starting_datetime_str)
        end_time = parser.parse(ending_datetime_str)

        # Convert the datetime to the local timezone
        start_time = start_time.astimezone(la_timezone)
        end_time = end_time.astimezone(la_timezone)

        # Ignore events that have already happened
        # NOTE: this would only miss events that have been added during the day and are taking place in the same day.
        #       (Assuming a 24-hour cycle of checking for new events)
        if start_time < datetime.now().astimezone(la_timezone):
            continue

        # Get the title of the event
        title_element = event.find(class_="card__title")
        title = title_element.text
        title = title.strip()

        # Get the description of the event by using the href inside the title
        event_url = title_element.find("a")["href"]

        # Get the html for the event page
        event_page_html = requests.get(main_site_url + event_url).text
        event_page_soup = BeautifulSoup(event_page_html, "html.parser")

        # Get the description of the event
        description_element = event_page_soup.find(
            class_="event-series--event__main-content"
        )

        # Get the description of the event
        description = description_element.text
        description = description.strip()

        # Remove any text after the first instance of three "="
        description = description.split("===")[0]

        is_quantum = "quantum" in title.lower()

        # Create the event json
        event_dict = {
            "summary": title,
            "location": zoom_url,
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
