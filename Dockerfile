FROM python:3.13 AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml ./uv.lock .python-version ./
RUN uv sync --frozen --no-cache

COPY . /app

RUN chmod +x entrypoint.sh && chmod +x setup_cron.sh

CMD ["/bin/bash", "-c", "./setup_cron.sh && ./entrypoint.sh"]
