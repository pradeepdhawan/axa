FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD . /AUMServer
WORKDIR /AUMServer

ENV AUM_SERVER_PORT=7777

CMD ./aumserver.py