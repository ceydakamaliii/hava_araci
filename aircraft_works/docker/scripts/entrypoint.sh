#!/bin/bash
python manage.py migrate && gunicorn --bind 127.0.0.1:8000 --workers 2 -t 120 aircraft.wsgi