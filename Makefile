ENV = $(CURDIR)/.venv
PYTHON3 = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip
PIP_COMPILE = $(ENV)/bin/pip-compile
PIP_SYNC = $(ENV)/bin/pip-sync

.PHONY: clean
clean:
	rm -rf $(ENV)
	rm -rf dist
	rm -rf .coverage htmlcov
	find -name '__pycache__' -print0 | xargs -0 rm -rf
	find -name '*.~*' -delete

$(ENV):
	virtualenv $(ENV) --python=python3
	$(PIP) install pip-tools

.PHONY: pip-compile
pip-compile: $(ENV)
	${PIP_COMPILE} -o requirements.txt pyproject.toml

.PHONY: pip-sync
pip-sync: $(ENV)
	${PIP_SYNC} requirements.txt

.PHONY: bootstrap
bootstrap: $(ENV)
	${PIP_SYNC} requirements.txt
