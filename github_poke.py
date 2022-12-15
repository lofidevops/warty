# SPDX-FileCopyrightText: Copyright 2022 Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os

from dotenv import load_dotenv
from github3 import login as github_login  # https://github3.readthedocs.io

if __name__ == "__main__":

    load_dotenv()
    CANONICAL_EMAIL = os.getenv("CANONICAL_EMAIL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_TOPIC = os.getenv("GITHUB_TOPIC")

    logging.info("Accessing GitHub")
    github = github_login(token=GITHUB_TOKEN)
    org = github.organization(GITHUB_OWNER)

    # # This takes tooooo long
    # logging.info("Iterating over GitHub repositories")
    # for repo in org.repositories():
    #     if GITHUB_TOPIC in repo.topics().names:
    #         pass  # this takes a long time

    results = github.search_repositories(f"org:{GITHUB_OWNER} topic:{GITHUB_TOPIC}")
    for repo in results:
        print(repo.name)
