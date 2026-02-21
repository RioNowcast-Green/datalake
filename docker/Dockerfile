FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MOZ_HEADLESS=1

ENV GECKODRIVER_VERSION=0.34.0

RUN apt-get update && apt-get install -y \
  firefox-esr \
  wget \
  curl \
  unzip \
  libgtk-3-0 \
  libdbus-glib-1-2 \
  libasound2 \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libxtst6 \
  libnss3 \
  libxss1 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  fonts-liberation \
  && wget -q https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz \
  && tar -xzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz \
  && mv geckodriver /usr/local/bin/ \
  && chmod +x /usr/local/bin/geckodriver \
  && rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-binary :all: -r requirements.txt

COPY . .

CMD ["python", "main.py"]
