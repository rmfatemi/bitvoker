FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml README.md poetry.lock* ./
COPY data/ /app/initial_data/
COPY bitvoker/ bitvoker/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8084 8085

# verify that a socket listening on port 8084 (0x1F94) exists without sending data
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD grep -q ':1F94' /proc/net/tcp || exit 1

COPY docker/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD ["bash", "/app/entrypoint.sh"]
