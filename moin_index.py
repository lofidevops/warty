import os
import urllib.parse
from time import sleep
from typing import Set

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def get_soup(url, cookies):
    sleep(1)
    text = requests.get(url, cookies=cookies).text
    # https://stackoverflow.com/questions/31554771/how-to-use-cookies-in-python-requests
    # https://stackoverflow.com/questions/13030095/how-to-save-requests-python-cookies-to-a-file

    return BeautifulSoup(text, features="html.parser")


def trim_at_first(character, text):
    location = text.find(character)

    if location == -1:
        return text
    else:
        return text[:location]


def get_base_links(cookies, page_url, base_url) -> Set[str]:
    link_set = set()
    soup = get_soup(page_url, cookies)
    all_links = soup.find_all("a")
    for link in all_links:
        link_url = urllib.parse.urljoin(base_url, link.get("href", ""))
        if link_url.startswith(base_url):
            link_url = trim_at_first("#", link_url)
            link_url = trim_at_first("?", link_url)
            link_set.add(link_url)

    return link_set


def convert_link_to_filename(page_url, base_url):
    if not page_url.startswith(base_url):
        raise ValueError("Invalid link.")

    if page_url == base_url:
        return "index"

    base_length = len(base_url)
    return page_url[base_length:].replace("/", "")


def invoke():
    # get environment variables
    load_dotenv()
    index_url = os.getenv("MOIN_INDEX", "https://example.com")
    base_url = os.getenv("MOIN_BASE", "https://example.com")
    cookies = {"MOIN_SESSION_443_ROOT": os.getenv("MOIN_SESSION_443_ROOT", "NOT-DEFINED")}

    index_links = get_base_links(cookies, index_url, base_url)

    with open("working/index.links", "w") as f:
        f.writelines("\n".join(sorted(index_links)))


if __name__ == "__main__":
    invoke()
