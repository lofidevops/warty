# SPDX-FileCopyrightText: Copyright 2022 Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from time import sleep

import requests
from dotenv import load_dotenv


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
    base_url = os.getenv("MOIN_BASE", "https://example.com")
    cookies = {
        "MOIN_SESSION_443_ROOT": os.getenv("MOIN_SESSION_443_ROOT", "NOT-DEFINED")
    }

    with open("working/index.links", "r") as f:
        all_links = [link.strip() for link in f.readlines()]

    # get all raw moinmoin

    for link in sorted(all_links):
        filename = convert_link_to_filename(link, base_url)
        sleep(3)
        text = requests.get(f"{link}?action=raw", cookies=cookies).text
        with open(f"./working/moin/{filename}.moin", "w") as f:
            f.writelines(text)


if __name__ == "__main__":
    invoke()
