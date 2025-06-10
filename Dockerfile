FROM node:18-alpine AS frontend-build

WORKDIR /app/web

COPY web/package*.json ./

RUN npm install --no-cache

COPY web/public ./public
COPY web/src ./src

RUN npm run build

FROM python:3.11-alpine

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN apk update && \
    apk add --no-cache openssl && \
    apk add --no-cache --virtual .build-deps gcc build-base && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --without dev --no-root && \
    apk del .build-deps

COPY bitvoker/ bitvoker/
COPY data/ /app/initial_data/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

COPY --from=frontend-build /app/web/build /app/web/build

EXPOSE 8083 8084 8085 8086

# verify that a socket listening on port 8084 (0x1F94) exists without sending data
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD grep -q ':1F94' /proc/net/tcp || exit 1

CMD ["sh", "/app/entrypoint.sh"]
