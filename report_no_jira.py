"""Generate a scary report of GH and LP tickets with no Jira references."""
import datetime
import io
import os
import tempfile
from typing import List
from dateutil.tz import tzutc

import chevron
import humanfriendly
from dotenv import load_dotenv
from github3 import login as github_login  # https://github3.readthedocs.io
from pydantic import BaseModel
from launchpadlib.launchpad import Launchpad  # https://launchpadlib.readthedocs.io

from wartlib.remote import publish_file


class ReportIssue(BaseModel):
    number: str
    path: str
    title: str
    created: datetime.datetime

    @property
    def age(self):
        delta = datetime.datetime.now(tz=tzutc()) - self.created
        return humanfriendly.format_timespan(delta.total_seconds(), max_units=1)


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
    def issues_youngest_first(self):
        return sorted(self.issues, key=lambda element: element.created, reverse=True)


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
    load_dotenv()

    GITHUB_EXTRAS = os.getenv("GITHUB_EXTRAS")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_TOPIC = os.getenv("GITHUB_TOPIC")

    LAUNCHPAD_GROUP = os.getenv("LAUNCHPAD_GROUP")

    REMOTE_ROOT = os.getenv("REMOTE_ROOT")
    REMOTE_SERVER = os.getenv("REMOTE_SERVER")
    REMOTE_USER = os.getenv("REMOTE_USER")

    repositories = []

    github = github_login(token=GITHUB_TOKEN)

    github_results = github.search_repositories(
        f"org:{GITHUB_OWNER} topic:{GITHUB_TOPIC}"
    )
    for r in github_results:
        repositories.append(repo_from_github(r.repository))

    for full_name in GITHUB_EXTRAS.split(","):
        owner, repo_name = full_name.split("/")
        repositories.append(repo_from_github(github.repository(owner, repo_name)))

    not_complete = [
        "New",
        "Incomplete",
        "Confirmed",
        "Triaged",
        "In Progress",
        "Fix Committed",
    ]
    # equivalent to lp_result.is_complete

    launchpad = Launchpad.login_with("warty", "production", version="devel")
    lp_group = launchpad.project_groups[
        LAUNCHPAD_GROUP
    ]  # https://launchpad.net/+apidoc/devel.html#project_group
    launchpad = ReportRepository(
        host="launchpad", path=LAUNCHPAD_GROUP, title=LAUNCHPAD_GROUP
    )
    for lp_result in lp_group.searchTasks(status=not_complete):
        _bug = lp_result.bug  # https://launchpad.net/+apidoc/devel.html#bug

    data = {"repositories": sorted(repositories, key=lambda element: element.title)}

    with open(
        "report_no_jira.mustache", "r"
    ) as template, tempfile.TemporaryDirectory() as d, io.open(
        f"{d}/report_no_jira.html", "w", encoding="utf8"
    ) as f:
        output = chevron.render(template, data)
        f.write(output)
        f.close()
        publish_file(
            f.name,
            REMOTE_SERVER,
            REMOTE_USER,
            f"{REMOTE_ROOT}/reports/report_no_jira.html",
        )
