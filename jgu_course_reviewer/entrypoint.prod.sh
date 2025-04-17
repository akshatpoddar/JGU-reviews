#!/usr/bin/env bash

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
python3 -m gunicorn --bind 0.0.0.0:8080 --workers 3 jgu_course_reviewer.wsgi:application