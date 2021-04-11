FROM wrwrwr/flask-scipy
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
COPY run.sh /etc/service/app/run
RUN chmod -R 755 /etc/service/app/run
