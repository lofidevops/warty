import os
import shutil
from pathlib import Path
import mdformat

import sh
from dotenv import load_dotenv

MOIN_BASE = None


def sed(pattern, filepath):
    sh.sed("-i", pattern, filepath)  # noqa


def pandoc(in_path, out_path):
    sh.pandoc("-f", "mediawiki", "-t", "commonmark", "-o", out_path, in_path)  # noqa


def frontmatter(title):
    return f"""---
layout: page
title: {title}
---

"""


def good_file(filepath):
    bad_starts = ["<!DOCTYPE", "#REDIRECT"]

    with open(filepath, "r") as f:
        first_line = f.readlines()[0]
        for bad in bad_starts:
            if first_line.startswith(bad):
                return False

    return True


def convert(moin_path):
    name = str(moin_path).replace("working/moin/", "").replace(".moin", "")
    mw_path = str(moin_path).replace("/moin", "/mediawiki").replace(".moin", ".wiki")
    cm_path = str(moin_path).replace("/moin", "/commonmark").replace(".moin", ".md")
    shutil.copy(moin_path, mw_path)

    sed("s/^ \*/*/g", mw_path)  # noqa
    sed("s/^  \*/**/g", mw_path)  # noqa
    sed("s/^   \*/***/g", mw_path)  # noqa
    sed("s/{{{/<pre>/g", mw_path)  # noqa
    sed("s/}}}/<\/pre>/g", mw_path)  # noqa

    for x in range(1, 12):
        sed(f"s/^ {x}. /# /g", mw_path)
        sed(f"s/^  {x}. /## /g", mw_path)

    pandoc(mw_path, cm_path)
    mdformat.file(cm_path, options={"wrap": "no", "number": True})

    with open(cm_path, "r") as f:
        content = frontmatter(name) + "".join(f.readlines())
        content = content.replace(' "wikilink")', ")")
        content = content.replace("\<\<TableOfContents()>>\n\n", "")  # noqa
        content = content.replace("\`", "`")  # noqa
        content = content.replace(f"{MOIN_BASE}/", "")
        content = content.replace(f"{MOIN_SPECIAL}", "")

    with open(cm_path, "w") as f:
        f.write(content)


if __name__ == "__main__":

    load_dotenv()
    MOIN_BASE = os.getenv("MOIN_BASE")
    MOIN_SPECIAL = os.getenv("MOIN_SPECIAL")

    for p in sorted(Path("./working/moin").glob("*.moin")):
        if good_file(p):
            convert(p)
