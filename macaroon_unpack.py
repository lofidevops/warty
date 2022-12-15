# SPDX-FileCopyrightText: Copyright 2022 Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unpack a macaroon file and inspect."""
import base64
import json
import os.path
import sys

import pymacaroons


def unmacaroon(value):
    return pymacaroons.Macaroon.deserialize(value).inspect()


def unpack(path):
    with open(path, mode="r") as file:
        content = file.read()

    content = base64.b64decode(content)
    content = json.loads(content)

    t = content["t"]
    root = unmacaroon(content["v"]["r"])
    discharge = unmacaroon(content["v"]["d"])

    print(f"\nt:\n{t}")
    print(f"\nroot (v.r):\n{root}")
    print(f"\ndischarge (v.d):\n{discharge}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        exit("Expecting exactly one argument.")

    path_argument = sys.argv[1]

    if not os.path.exists(path_argument):
        exit(f"Path {path_argument} does not exist.")

    unpack(path_argument)
