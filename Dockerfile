FROM python:3.13 AS base
RUN apt-get update && apt-get install -y vim cron

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV PYTHONPATH=/app

COPY pyproject.toml ./uv.lock .python-version ./
RUN uv sync

COPY . /app

RUN chmod +x entrypoint.sh

CMD ["/bin/bash", "-c", "./entrypoint.sh"]
