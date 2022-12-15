# SPDX-FileCopyrightText: Copyright 2022 Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Environment:
    def _yield_variables(self):
        for a in dir(self):
            if a[0] != "_" and a.isupper():
                yield a

    def set_environment(self):
        load_dotenv()
        for f in self._yield_variables():
            self.__setattr__(f, os.getenv(f, None))

    def validate(self):
        missing = []
        for a in self._yield_variables():
            value = self.__getattribute__(a)
            if value is None or value == "":
                missing.append(a)

        if len(missing) == 0:
            return True
        else:
            print(f"Missing: {missing}")
            return False
