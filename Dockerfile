FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /code

COPY . /code

RUN apt update && \
    apt install -y --assume-yes python3-dev libpq-dev build-essential python3-pip libgeos-dev && \
    pip3 install -r requirements.txt
