export PROJECT_NAME = afpy

VENV = $(PWD)/.env
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python
FLASK = $(VENV)/bin/flask

all: install serve

install:
	test -d $(VENV) || virtualenv $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -e .

clean:
	rm -fr dist
	rm -fr $(VENV)
	rm -fr *.egg-info

check-outdated:
	$(PIP) list --outdated --format=columns

serve:
	$(VENV)/bin/$(PROJECT_NAME).py
