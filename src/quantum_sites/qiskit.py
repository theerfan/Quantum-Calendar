import re
from datetime import datetime, timedelta

import requests
from dateutil import parser
import json

from .util import la_timezone, eastern_timezone, get_soup, get_main_website

from typing import List

init_url = "https://qiskit.org/events/seminar-series/"
main_url = get_main_website(init_url)


def get_events() -> List[dict]:
    events_list = []

    html_soup = get_soup(init_url)

    # Get the link tag with rel="modulepreload"
    # And then get the value of its href attribute
    # Which is the URL of the initializer JS file
    init_js_url = main_url
    init_js_url += html_soup.find("link", {"rel": "modulepreload"})["href"]

    init_js_file = requests.get(init_js_url).text

    # Find the name of the data JS file in the text
    # Which starts with `"./seminar-series` and ends with `.js`
    data_js_filename = re.search(r'"\.\/seminar-series(.*)\.js"', init_js_file).group(0)

    # Get the value between the first two quotes
    # And then remove the ./ from the start
    data_js_filename = data_js_filename.split('"')[1][2:]

    # The URL of the data JS file
    data_js_url = f"{main_url}/_nuxt/{data_js_filename}"

    # Qiskit sends their data through a fixed js file :)))))
    nuxt_js_text = requests.get(data_js_url).text

    # Find the part of the JS file that is between `q = ` and `T =`
    # Which is the JSON string we want
    json_string = re.search(r"q=(.*)T=", nuxt_js_text).group(1)

    # Remove the trailing comma
    json_string = json_string[:-1]

    # Parse a json string where the keys are not in quotes
    json_string = re.sub(r"([{,])\s*(\w+)\s*:", r'\1"\2":', json_string)
    
    # Convert the string to a dictionary
    json_dict = json.loads(json_string)

    for event in json_dict:
        title = event["title"]
        title = re.sub(r"\s+", " ", title).strip()

        try:
            start_time = parser.parse(event["date"])
        except:
            start_time = parser.parse(event["startDate"])

        # Change the hour to 12:00 PM
        start_time = start_time.replace(hour=12, minute=0, second=0, microsecond=0)

        # Set the default timezone to Eastern
        start_time = eastern_timezone.localize(start_time)

        # Convert the time to Los Angeles time
        start_time = start_time.astimezone(la_timezone)

        end_time = start_time + timedelta(hours=2)

        # Ignore events that have already happened
        if start_time < datetime.now().astimezone(la_timezone):
            continue

        description = event["abstract"]

        location = event["to"]

        # Create the event json
        event_dict = {
            "summary": title,
            "location": location,
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


if __name__ == "__main__":
    events = get_events()
    print(events)
