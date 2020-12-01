FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD . /Controller
WORKDIR /Controller

ENV FILL_SERVER_TOPIC=FILLS

CMD ./controller.py