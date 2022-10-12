BOOT_TASKS = bootstrap pip-sync
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

## same action for bootstrap and pip-sync
.PHONY: $(BOOT_TASKS)
$(BOOT_TASKS): $(ENV)
	${PIP_SYNC} requirements.txt

## see https://stackoverflow.com/questions/6273608
.PHONY: run
run: $(ENV)
	${PYTHON3} $(filter-out $@,$(MAKECMDGOALS))
