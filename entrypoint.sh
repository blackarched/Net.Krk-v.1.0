#!/bin/bash

# Create captures directory if it doesn't exist
mkdir -p captures

# Start the Gunicorn server.
# It will listen on the host and port specified by the environment variables.
echo "Starting net.krak on ${API_HOST}:${API_PORT}..."
exec gunicorn --bind ${API_HOST}:${API_PORT} --workers 1 --threads 4 dashboard_api:app