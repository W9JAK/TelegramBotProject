FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Etc/UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /code

RUN apt update && \
    apt install -y --no-install-recommends python3-dev libpq-dev build-essential python3-pip libgeos-dev cron curl && \
    pip3 install -r requirements.txt

RUN curl -s https://rclone.org/install.sh | bash

COPY . /code

COPY config/rclone.conf /root/.config/rclone/rclone.conf

COPY main/crontab /etc/cron.d/orders-to-excel-cron
RUN chmod 0644 /etc/cron.d/orders-to-excel-cron \
    && crontab /etc/cron.d/orders-to-excel-cron \
    && touch /var/log/cron.log

# Запуск cron и главного приложения
CMD cron && python3 main/run.py
