# Warty scripts 🐗

Lower your expectations. Lower.

## Development environment

- Initialise Python environment:

  ```
  make bootstrap
  .venv/bin/activate  # pick script for your shell
  ```

## MoinMoin conversion

### Set up environment

- Log into https://wiki.ubuntu.com/BugSquad/KnowledgeBase

- Extract the value MOIN_SESSION_443_ROOT from your session cookie.

- Create `.env` as follows:

  ```
  MOIN_SESSION_443_ROOT=abcdefghijklmnopqrstuvwxyz
  MOIN_BASE=https://wiki.ubuntu.com/BugSquad/KnowledgeBase
  MOIN_TAIL=BugSquad/KnowledgeBase
  ```

### Create index

```
python moin_index.py
# creates new file index.links
```

### Pull MoinMoin pages

```
python moin_pull.py
# stores files in ./raw_moin/
```

## Convert MoinMoin pages

```
python moin_convert.py
# stores intermediary files in ./mediawiki/
# stores final version in ./commonmark/
```

## Copying

Copyright 2022 Canonical \
SPDX-License-Identifier: GPL-3.0-or-later \
Please observe the Ubuntu Code Of Conduct.
