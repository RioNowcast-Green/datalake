FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV MOZ_HEADLESS=1

RUN apt-get update && apt-get install -y \
  cron \
  firefox-esr \
  libgtk-3-0 \
  libnss3 \
  fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

COPY cron/crontab /etc/cron.d/app-cron
RUN chmod 0644 /etc/cron.d/app-cron \
  && crontab /etc/cron.d/app-cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]
