"""Generate a scary report of GH and LP tickets with no Jira references."""
import datetime
import logging
import os
from typing import List

import humanfriendly
from dateutil.tz import tzutc
from dotenv import load_dotenv
from github3 import login as github_login  # https://github3.readthedocs.io
from launchpadlib.launchpad import Launchpad  # https://launchpadlib.readthedocs.io
from pydantic import BaseModel

from wartlib.remote import publish_report


class ReportIssue(BaseModel):
    number: str
    path: str
    title: str
    created: datetime.datetime
    jira: str = ""

    @property
    def age(self):
        delta = datetime.datetime.now(tz=tzutc()) - self.created
        return humanfriendly.format_timespan(delta.total_seconds(), max_units=1)

    @property
    def jira_link(self):
        return f"{JIRA_BASE_URL}/{self.jira}"


class ReportRepository(BaseModel):
    host: str
    path: str
    title: str
    issues: List[ReportIssue] = []

    @property
    def icon(self):
        if self.host == "github":
            return "🐙"
        elif self.host == "launchpad":
            return "🚀"
        else:
            return "💾"

    @property
    def issues_with_jira_youngest_first(self):
        return sorted(
            filter(lambda f: f.jira != "", self.issues),  # issues with jira reference
            key=lambda s: s.created,
            reverse=True,
        )  # sorted by creation date

    @property
    def issues_without_jira_youngest_first(self):
        return sorted(
            filter(
                lambda f: f.jira == "", self.issues
            ),  # issues without jira reference
            key=lambda s: s.created,
            reverse=True,
        )  # sorted by creation date


def repo_from_github(github_repo):
    report_repo = ReportRepository(
        host="github", path=github_repo.html_url, title=github_repo.name
    )

    for issue in github_repo.issues(state="open"):
        report_issue = ReportIssue(
            number=str(issue.number),
            path=issue.html_url,
            title=issue.title,
            created=issue.created_at,
        )
        report_repo.issues.append(report_issue)

    return report_repo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    GITHUB_EXTRAS = os.getenv("GITHUB_EXTRAS")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_TOPIC = os.getenv("GITHUB_TOPIC")

    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_PROJECT_CODE = os.getenv("JIRA_PROJECT_CODE")

    LAUNCHPAD_GROUP = os.getenv("LAUNCHPAD_GROUP")

    REMOTE_ROOT = os.getenv("REMOTE_ROOT")
    REMOTE_SERVER = os.getenv("REMOTE_SERVER")
    REMOTE_USER = os.getenv("REMOTE_USER")

    logging.info("Initializing. Including remote resource connections.")
    results = []
    github = github_login(token=GITHUB_TOKEN)
    launchpad = Launchpad.login_with("warty", "production", version="devel")

    # GitHub repositories matching organisation and topic
    logging.info("Processing GitHub repositories.")
    github_results = github.search_repositories(
        f"org:{GITHUB_OWNER} topic:{GITHUB_TOPIC}"
    )
    for r in github_results:
        results.append(repo_from_github(r.repository))

    # additional GitHub repositories listed in GITHUB_EXTRAS
    logging.info("Processing extra GitHub repositories.")
    for full_name in GITHUB_EXTRAS.split(","):
        owner, repo_name = full_name.split("/")
        results.append(repo_from_github(github.repository(owner, repo_name)))

    # Launchpad issues matching LAUNCHPAD_GROUP
    logging.info("Processing Launchpad issues.")
    lp_group = launchpad.project_groups[
        LAUNCHPAD_GROUP
    ]  # https://launchpad.net/+apidoc/devel.html#project_group
    launchpad = ReportRepository(
        host="launchpad", path=LAUNCHPAD_GROUP, title=LAUNCHPAD_GROUP
    )

    not_complete = [
        "New",
        "Incomplete",
        "Confirmed",
        "Triaged",
        "In Progress",
        "Fix Committed",
    ]
    # equivalent to lp_result.is_complete

    for lp_result in lp_group.searchTasks(status=not_complete):
        _bug = lp_result.bug  # https://launchpad.net/+apidoc/devel.html#bug

    # generate data object
    data = {"repositories": sorted(results, key=lambda element: element.title)}

    # publish reports
    logging.info("Publishing reports.")
    publish_report(
        "report_jira_link_missing.mustache",
        data,
        "report_jira_link_missing.html",
        REMOTE_SERVER,
        REMOTE_USER,
        REMOTE_ROOT,
    )

    publish_report(
        "report_jira_link_exists.mustache",
        data,
        "report_jira_link_exists.html",
        REMOTE_SERVER,
        REMOTE_USER,
        REMOTE_ROOT,
    )
