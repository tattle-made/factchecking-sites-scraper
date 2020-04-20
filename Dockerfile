FROM python:3.7
LABEL maintainer "Tattle Civic Technologies <admin@tattle.co.in>"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV FLASK_ENV=docker
EXPOSE 5000
CMD python server.py