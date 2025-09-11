#!/bin/bash
# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Change to that directory and start docker-compose in detached mode
cd "$DIR" && sudo docker-compose up -d