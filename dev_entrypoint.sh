#!/bin/sh
export FLASK_APP=financial/__init__.py
pipenv run flask --debug run -h 0.0.0.0 -p 5000
