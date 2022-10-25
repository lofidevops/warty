import os

from jira import JIRA  # https://jira.readthedocs.io
from launchpadlib.launchpad import Launchpad  # https://launchpadlib.readthedocs.io
from github3 import login as github_login  # https://github3.readthedocs.io

from dotenv import load_dotenv

if __name__ == "__main__":

    load_dotenv()
    CANONICAL_EMAIL = os.getenv("CANONICAL_EMAIL")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_CODE = os.getenv("JIRA_PROJECT_CODE")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")

    jira = JIRA(JIRA_BASE_URL, basic_auth=(CANONICAL_EMAIL, JIRA_API_TOKEN))
    jira_result = jira.search_issues(f'project={JIRA_PROJECT_CODE}')
    for jira_issue in jira_result:
        print(jira_issue.key)

    launchpad = Launchpad.login_with('warty', 'production', version='devel')

    bug_one = launchpad.bugs[1]
    print(bug_one.title)

    github = github_login(token=GITHUB_TOKEN)
    repo = github.repository(owner=GITHUB_OWNER, repository="acceptable")
    for gh_issue in repo.issues(state="open"):
        print(gh_issue.title)
