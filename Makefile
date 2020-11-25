VENV = $(PWD)/venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python
FLASK = $(VENV)/bin/flask
ISORT = $(VENV)/bin/isort
BLACK = $(VENV)/bin/black

all: install serve

install:
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -r requirements.txt -r requirements-dev.txt

clean:
	rm -fr $(VENV)

check-outdated:
	$(PIP) list --outdated --format=columns

test:
	$(PYTHON) -m pytest tests.py afpy/ --flake8 --black --cov=afpy --cov=tests --cov-report=term-missing

serve:
	$(PYTHON) run.py

.PHONY: all install clean check-outdated test serve
