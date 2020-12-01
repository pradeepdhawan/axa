FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD . /FillServer
WORKDIR /FillServer

ENV FILL_SERVER_PORT=9999

CMD ./fillserver.py