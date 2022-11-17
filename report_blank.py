"""Publish a blank report."""

import os
import tempfile

from dotenv import load_dotenv

from wartlib.remote import publish_file

if __name__ == "__main__":
    load_dotenv()
    REMOTE_USER = os.getenv("REMOTE_USER")
    REMOTE_SERVER = os.getenv("REMOTE_SERVER")
    REMOTE_ROOT = os.getenv("REMOTE_ROOT")

    with tempfile.NamedTemporaryFile() as f:
        publish_file(
            f.name, REMOTE_SERVER, REMOTE_USER, f"{REMOTE_ROOT}/reports/blank.html"
        )
