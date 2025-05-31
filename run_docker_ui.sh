#!/bin/bash

# Build and run the HTML interface with test API
docker-compose -f docker-compose.html.yml up --build

# To run in detached mode, uncomment the following line
# docker-compose -f docker-compose.html.yml up --build -d