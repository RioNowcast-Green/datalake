FROM python:3.11-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MOZ_HEADLESS=1

# Dependências do Firefox + Selenium
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
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Comando padrão (PROD)
CMD ["python", "main.py"]
