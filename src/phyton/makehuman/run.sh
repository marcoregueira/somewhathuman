#!/usr/bin/env bash


cd /app


if [ "$FLASK_ENV" == "development" ]; then
        python app.py
else
        gunicorn --config /etc/gunicorn/config.py app:app
fi