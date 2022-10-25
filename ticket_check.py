import os

# from jira import JIRA  # https://jira.readthedocs.io
from launchpadlib.launchpad import Launchpad  # https://launchpadlib.readthedocs.io
from github3 import login as github_login  # https://github3.readthedocs.io

from dotenv import load_dotenv

GH_REPO_LIST = ["acceptable", "surl"]

if __name__ == "__main__":

    missing = set()

    load_dotenv()
    CANONICAL_EMAIL = os.getenv("CANONICAL_EMAIL")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_PROJECT_CODE = os.getenv("JIRA_PROJECT_CODE")
    LAUNCHPAD_GROUP = os.getenv("LAUNCHPAD_GROUP")

    github = github_login(token=GITHUB_TOKEN)

    for name in GH_REPO_LIST:
        gh_repo = github.repository(owner=GITHUB_OWNER, repository=name)
        for gh_issue in gh_repo.issues(state="open"):
            if JIRA_BASE_URL not in gh_issue.body_text:
                missing.add(gh_issue.html_url)

    # search_status = {'Incomplete', 'New', 'Triaged', 'In Progress', 'Confirmed'}  # ignore 'Fix Committed'

    launchpad = Launchpad.login_with('warty', 'production', version='devel')
    lp_group = launchpad.project_groups[LAUNCHPAD_GROUP]  # https://launchpad.net/+apidoc/devel.html#project_group
    for lp_result in lp_group.searchTasks():
        if not lp_result.is_complete:
            _bug = lp_result.bug  # https://launchpad.net/+apidoc/devel.html#bug
            if JIRA_BASE_URL not in _bug.description:
                missing.add(_bug.web_link)

    print("These issues are missing a JIRA link:")
    print(" * " + "\n * ".join(missing))
