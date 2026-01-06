#!/bin/bash

# Stop and remove existing container if it exists
docker stop postgres-dev 2>/dev/null
docker rm postgres-dev 2>/dev/null

# Run new Postgres container
# Matches credentials in app/core/config.py
docker run -d \
  --name postgres-dev \
  -p 5435:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=invoice_doc \
  -e POSTGRES_DB=invoice_doc \
  postgres:15-alpine

echo "Postgres container 'postgres-dev' started on port 5435."
