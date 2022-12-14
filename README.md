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

# Copying

Warty scripts 🐗 \
<https://github.com/lofidevops/warty> \
Copyright 2022 Canonical Ltd \
SPDX-License-Identifier: GPL-3.0-or-later

Shared under GPL-3.0-or-later. We adhere to the Ubuntu Code of Conduct 2.0, and
certify origin per DCO 1.1 with a signed-off-by line. Contributions under the
same terms are welcome.

Submit security and conduct issues as private tickets. Sign commits with
`git commit --signoff`. For a software bill of materials run `reuse spdx`. For
more details see LICENSES, CONDUCT and DCO.
