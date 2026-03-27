#!/usr/bin/env bash

if [ -z "$(ls -A /app/data)" ]; then
    cp -R /app/initial_data/* /app/data/
fi

chown -R appuser:appgroup /app/data

exec su-exec appuser python -m bitvoker.server
