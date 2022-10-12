import os
import re
from typing import Iterator, Tuple

COMMONMARK_PATH = os.getenv("COMMONMARK_PATH")
BASE_URL = os.getenv("BASE_URL")
SHORT_URL = os.getenv("SHORT_URL")


def cm2moin_single_line(line, code_block) -> Tuple[str, bool]:

    if line == "```" and code_block:
        # end code block
        return "}}}", False

    elif line == "```" and not code_block:
        # start code block
        return "{{{", True

    elif code_block:
        # line in code block
        return line, True

    elif line.startswith("# "):
        header = "= " + line[2:] + " ="
        return header, False

    elif line.startswith("## "):
        header = "== " + line[3:] + " =="
        return header, False

    elif line.startswith("**") and line.endswith("**"):
        bold = "'''" + line[2:-2] + "'''"
        return bold, False

    elif line.startswith("*") and line.endswith("*"):
        italic = "''" + line[1:-1] + "''"
        return italic, False

    else:
        paragraph = line

        if line.startswith("* "):  # lists must start with a space
            paragraph = " " + paragraph

        all_links = re.findall(r"\[.*?]\(.*?\)", line)  # find all [aaa](zzz)
        for cm_link in all_links:
            name, target = cm_link[1:-1].split("](")
            moin_link = f"[[{target}|{name}]]"
            paragraph = paragraph.replace(cm_link, moin_link)

        # fix hard links
        paragraph = paragraph.replace(
            f"{BASE_URL}", f"{SHORT_URL}"
        )

        return paragraph, False


def cm2moin_all_lines(all_lines) -> Iterator[str]:
    code_block = False
    for line in all_lines:
        converted_line, code_block = cm2moin_single_line(line.rstrip(), code_block)
        yield converted_line + "\n"


if __name__ == "__main__":
    if not COMMONMARK_PATH.endswith(".md"):
        raise ValueError(f"{COMMONMARK_PATH} does not end with .md")

    moin_path = COMMONMARK_PATH[:-3] + ".moin"

    with open(COMMONMARK_PATH, "r") as cm_file:
        result = cm2moin_all_lines(cm_file.readlines())

    with open(moin_path, "w") as moin_file:
        moin_file.writelines(result)
