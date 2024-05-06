FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Etc/UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /code
COPY . /code

RUN apt update && \
    apt install -y --no-install-recommends python3-dev libpq-dev build-essential python3-pip libgeos-dev cron && \
    pip3 install -r requirements.txt

COPY crontab /etc/cron.d/orders-to-excel-cron
RUN chmod 0644 /etc/cron.d/orders-to-excel-cron \
    && crontab /etc/cron.d/orders-to-excel-cron \
    && touch /var/log/cron.log

CMD cron && python3 main/run.py

