# Quantum  Calendar

A simple Python script to get new events from Quantum institutes from all around the world and add them to a Google Calendar.

The list of insitutes currently includes:
- UC Berkeley's Simons Institute's [Calendar](https://simons.berkeley.edu/programs-events/public-lectures)
- Waterloo's IQC [Events](https://uwaterloo.ca/institute-for-quantum-computing/events)
- Qiskit's [Seminar Series](https://qiskit.org/events/seminar-series/)

To add your own `credentials.json` and `token.json` files, follow the instructions [here](https://developers.google.com/calendar/api/quickstart/python).

Link to the (Google) [Quantum Calendar](https://calendar.google.com/calendar/embed?src=622f4caddb463f8133610024ea9cca499979bab404b6e99a246bf0e95f567152%40group.calendar.google.com&ctz=America%2FLos_Angeles).

To-do list:
1. There is no database, it just cross-checks the events with the calendar. I could add a database of event title's hashes to avoid this checking that will grow heavily with the number of events.
2. Add more institutes to the list.


---

To the person at Qiskit who keeps changing their website and breaking my code: 
Please sir/madam, stop doing it. :))