# SPDX-FileCopyrightText: Copyright 2022 Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

from wartlib.environment import Environment


@dataclass
class HelloEnvironment(Environment):
    CANONICAL_EMAIL = ""


print("Hello world.")

E = HelloEnvironment()
E.set_environment()
E.validate()
print(E.CANONICAL_EMAIL)
