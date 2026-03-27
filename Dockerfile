FROM node:18-alpine AS frontend-build

WORKDIR /app/web

COPY web/package*.json ./

RUN npm install --no-cache

COPY web/public ./public
COPY web/src ./src

RUN npm run build

FROM python:3.11-alpine AS builder

RUN apk add --no-cache build-base

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY bitvoker/ bitvoker/
COPY README.md pyproject.toml ./

FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache openssl

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/bitvoker ./bitvoker
COPY --from=builder /app/README.md .
COPY --from=builder /app/pyproject.toml .

COPY data/ /app/initial_data/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

COPY --from=frontend-build /app/web/build /app/web/build

RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data /app/initial_data

EXPOSE 8083 8084 8085 8086

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD grep -q ':1F94' /proc/net/tcp || exit 1

USER appuser

CMD ["sh", "/app/entrypoint.sh"]
