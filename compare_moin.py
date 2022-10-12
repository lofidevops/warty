import os
from pprint import pprint

import requests
from bs4 import BeautifulSoup

URL1 = os.getenv("COMPARE1")
URL2 = os.getenv("COMPARE2")
MOIN_SESSION_443_ROOT = os.getenv("MOIN_SESSION_443_ROOT")


def get_soup(url, cookies):
    text = requests.get(url, cookies=cookies).text
    # https://stackoverflow.com/questions/31554771/how-to-use-cookies-in-python-requests
    # https://stackoverflow.com/questions/13030095/how-to-save-requests-python-cookies-to-a-file

    return BeautifulSoup(text, features="html.parser")


if __name__ == "__main__":

    addresses = {1: URL1, 2: URL2}

    cookies = {"MOIN_SESSION_443_ROOT": MOIN_SESSION_443_ROOT}

    soup = {}
    links = {1: set(), 2: set()}

    for soup_id, url in addresses.items():
        soup[soup_id] = get_soup(url, cookies)
        for link in soup[soup_id].find_all("a"):
            links[soup_id].add(link["href"])

    print("Tags from page 1 not found in page 2:")
    pprint(links[1].difference(links[2]))

    print("Tags from page 2 not found in page 1:")
    pprint(links[2].difference(links[1]))
