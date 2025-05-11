FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml README.md poetry.lock* ./

COPY bitvoker/ bitvoker/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8084 8085

CMD ["poetry", "run", "bitvoker"]
