from bs4 import BeautifulSoup
from pytz import timezone
import requests

def get_main_website(url: str):
    while url.count("/") > 2:
        url = url.rsplit("/", 1)[0]
    return url

def get_soup(url: str):
    # Use requests to get the html for this url
    response = requests.get(url)
    html = response.text
    
    # Use BeautifulSoup to parse the html
    soup = BeautifulSoup(html, "html.parser")
    return soup

la_timezone = timezone("America/Los_Angeles")

# I know these two are the same, but I'm keeping them separate just in case
eastern_timezone = timezone("US/Eastern")
toronto_timezone = timezone("America/Toronto")