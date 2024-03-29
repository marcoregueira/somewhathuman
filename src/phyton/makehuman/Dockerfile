FROM python:2.7.12

MAINTAINER wrwrwr <docker@wr.waw.pl>

# Install runit, and up-to-date Flask and SciPy from PyPI.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
        g++ \
        gcc \
        gfortran \
        libatlas3-base \
        libatlas-dev \
        liblapack3 \
        liblapack-dev \
        runit \
    && pip install --upgrade pip \
    && pip install \
        flask \
        gevent \
        gunicorn \
        scipy \
    && apt-get purge --yes --auto-remove \
        g++ \
        gcc \
        gfortran \
        libatlas-dev \
        liblapack-dev \
    && rm -rf \
        /root/.cache/* \
        /var/lib/apt/lists/*

# An example Gunicorn configuration (to be used through --config).
COPY gunicorn-config.py /etc/gunicorn/config.py

# The provided Gunicorn configuration specifies this port.
EXPOSE 80

# Add application start scripts as /etc/service/<app>/run:
#
#    COPY run.sh /etc/service/app/run
#
# The "run" script could contain something like:
#
#    #!/usr/bin/env bash
#
#    cd /app
#    gunicorn --config /etc/gunicorn/config.py app:app

COPY runit.sh /runit.sh
ENTRYPOINT ["/runit.sh"]


#FROM wrwrwr/flask-scipy
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY run.sh /etc/service/app/run
RUN chmod -R 755 /etc/service/app/run

ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=80
ENV FLASK_ENV=development

COPY . /app


