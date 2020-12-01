FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD . /PositionServer
WORKDIR /PositionServer

ENV FILL_SERVER_PORT=9999

CMD ./positionserver.py