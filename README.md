# Warty scripts 🐗

Run at your peril!

## Development environment

Initialise Python environment:

```
make bootstrap
```

Run a Python script:

```
make run hello.py
```

## MoinMoin conversion

### Set up environment

- Log into https://wiki.ubuntu.com/BugSquad/KnowledgeBase

- Extract the value MOIN_SESSION_443_ROOT from your session cookie.

- Create `.env` as follows:

  ```
  MOIN_SESSION_443_ROOT=abcdefghijklmnopqrstuvwxyz
  MOIN_BASE=https://wiki.ubuntu.com/BugSquad/KnowledgeBase
  MOIN_INDEX=https://wiki.ubuntu.com/BugSquad/KnowledgeBase/SubPages
  ```

### Create index

```
make run moin_index.py
# creates new file index.links
```

### Pull MoinMoin pages

```
make run moin_pull.py
# stores files in ./working/moin/
```

### Convert MoinMoin pages

```
make run moin_convert.py
cd working/commonmark
./postprocessing.sh
```

## Copying

Warty scripts 🐗 \
Copyright 2022 Canonical \
SPDX-License-Identifier: GPL-3.0-or-later \
Ubuntu Code of Conduct 2.0
