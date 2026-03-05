FROM python:3.13 AS base
RUN apt-get update && apt-get install -y \
    vim \
    cron \
    wget \
    gnupg2 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV PYTHONPATH=/app

COPY pyproject.toml ./uv.lock .python-version ./
RUN uv sync

COPY . /app

RUN chmod +x entrypoint.sh

CMD ["/bin/bash", "-c", "./entrypoint.sh"]
