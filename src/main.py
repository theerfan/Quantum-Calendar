import json
from datetime import datetime, timedelta

import pause

from gcalendar import add_events
from quantum_sites.berkeley import get_events as get_berkeley_events
from quantum_sites.iqc import get_events as get_iqc_events
from quantum_sites.qiskit import get_events as get_qiskit_events

from pytz import timezone

la_timezone = timezone("America/Los_Angeles")

all_get_events = [get_berkeley_events, get_iqc_events, get_qiskit_events]

def main():

    event_dicts = []

    # Add the event json to the list of event jsons
    for get_events in all_get_events:
        for event_json in get_events():
            event_dicts.append(event_json)
    
    print("Finished getting events")
    
    # Add the events to the calendar
    add_events(event_dicts)

    print("Finished adding events to the Google Calendar")


if __name__ == "__main__":
    while True:
        main()

        # Wait until the next day to check for new events
        start_of_today = (
            datetime.now().astimezone(la_timezone).replace(hour=0, minute=0, second=0)
        )
        start_of_tomorrow = start_of_today + timedelta(days=1)
        print(f"Pausing until {start_of_tomorrow} to check for new event")
        pause.until(start_of_tomorrow)
