#!/usr/bin/env bash
cd /app
gunicorn --config /etc/gunicorn/config.py app:app
