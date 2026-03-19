FROM python:3.13 AS base

ARG TARGETARCH

RUN apt-get update && apt-get install -y \
    vim \
    cron \
    wget \
    gnupg2 \
    && if [ "$TARGETARCH" = "amd64" ]; then \
         mkdir -p /usr/share/keyrings \
         && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
            | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
         && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" \
            > /etc/apt/sources.list.d/google-chrome.list \
         && apt-get update \
         && apt-get install -y google-chrome-stable; \
       elif [ "$TARGETARCH" = "arm64" ]; then \
         apt-get install -y chromium chromium-driver; \
       fi \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV PYTHONPATH=/app

COPY pyproject.toml ./uv.lock .python-version ./
RUN uv sync

COPY . /app

RUN chmod +x entrypoint.sh

CMD ["/bin/bash", "-c", "./entrypoint.sh"]
