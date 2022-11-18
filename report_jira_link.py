"""Generate a scary report of GH and LP tickets with no Jira references."""
import datetime
import fnmatch
import logging
import os
from typing import List

import humanfriendly
from dateutil.tz import tzutc
from dotenv import load_dotenv
from github3 import login as github_login  # https://github3.readthedocs.io
from jira import JIRA  # https://jira.readthedocs.io
from launchpadlib.launchpad import Launchpad  # https://launchpadlib.readthedocs.io
from pydantic import BaseModel

from wartlib.remote import publish_report


class ReportIssue(BaseModel):
    number: str
    path: str
    summary: str
    title: str
    created: datetime.datetime
    jira: str = ""
    backlink: bool = False

    def populate_jira(self):
        matches = fnmatch.filter(self.summary.split(), JIRA_TEXT_FILTER)
        if len(matches) != 0:
            self.jira = matches[0]
            self.backlink = check_jira_backlink(self.jira, self.path)

    @property
    def age(self):
        delta = datetime.datetime.now(tz=tzutc()) - self.created
        return humanfriendly.format_timespan(delta.total_seconds(), max_units=1)

    @property
    def jira_path(self):
        return f"{JIRA_BASE_URL}/browse/{self.jira}" if self.jira != "" else ""

    @property
    def jira_backlink_icon(self):
        return "" if self.backlink else "😢"


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
            summary=str(issue.body),
            created=issue.created_at,
        )
        report_issue.populate_jira()
        report_repo.issues.append(report_issue)

    return report_repo


def repo_from_launchpad(lp_target):
    return ReportRepository(
        host="launchpad", path=lp_target.web_link, title=lp_target.name
    )


def issue_from_launchpad(lp_bug):
    return ReportIssue(
        title=lp_bug.title,
        number=str(lp_bug.id),
        summary=lp_bug.description,
        created=lp_bug.date_created,
        path=lp_bug.web_link,
    )


def check_jira_backlink(jira_ref, source_link):
    issue = jira.issue(jira_ref)
    return source_link in issue.fields.description


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    CANONICAL_EMAIL = os.getenv("CANONICAL_EMAIL")

    GITHUB_EXTRAS = os.getenv("GITHUB_EXTRAS")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_TOPIC = os.getenv("GITHUB_TOPIC")

    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_TEXT_FILTER = os.getenv("JIRA_PROJECT_CODE") + "-*"
    JIRA_TEXT_EXAMPLE = os.getenv("JIRA_PROJECT_CODE") + "-1234"

    LAUNCHPAD_GROUP = os.getenv("LAUNCHPAD_GROUP")

    REMOTE_ROOT = os.getenv("REMOTE_ROOT")
    REMOTE_SERVER = os.getenv("REMOTE_SERVER")
    REMOTE_USER = os.getenv("REMOTE_USER")

    logging.info("Initializing. Including remote resource connections.")
    results = []
    github = github_login(token=GITHUB_TOKEN)
    jira = JIRA(JIRA_BASE_URL, basic_auth=(CANONICAL_EMAIL, JIRA_API_TOKEN))
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

    lp_projects = {}

    for lp_result in lp_group.searchTasks(status=not_complete):

        _bug = lp_result.bug
        _target = lp_result.target
        _target_link = _target.web_link
        if _target_link not in lp_projects:
            lp_projects[_target_link] = repo_from_launchpad(_target)

        lp_projects[_target_link].issues.append(issue_from_launchpad(_bug))

    # generate data object
    combined = results + list(lp_projects.values())
    data = {
        "jira_example": JIRA_TEXT_EXAMPLE,
        "repositories": sorted(combined, key=lambda element: element.title),
    }

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
