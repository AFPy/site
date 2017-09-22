VENV = $(PWD)/.env
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python
FLASK = $(VENV)/bin/flask
PYTEST = $(VENV)/bin/pytest

all: install serve

install:
	test -d $(VENV) || virtualenv $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -e .[test]

clean:
	rm -fr dist
	rm -fr $(VENV)
	rm -fr *.egg-info

check-outdated:
	$(PIP) list --outdated --format=columns

test:
	$(PYTEST) tests.py --flake8 --isort --cov=afpy --cov=tests

serve:
	$(VENV)/bin/afpy.py
