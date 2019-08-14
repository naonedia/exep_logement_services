#!/bin/bash

# Download OpenStreetMap data for openrouteservice
curl https://download.geofabrik.de/europe/france/pays-de-la-loire-latest.osm.pbf --output ./openrouteservice/docker/data/pays-de-la-loire-latest.osm.pbf

# Download OpenStreetMap data for openpoiservice
cp ./openrouteservice/docker/data/pays-de-la-loire-latest.osm.pbf ./openpoiservice/osm/

# Start OpenRouteService
docker-compose -f openrouteservice/docker/docker-compose.yml up -d 

# Start OpenPoiService
docker-compose -f openpoiservice/docker-compose.yml up -d 

# Import data
docker exec -it naonedia_gunicorn_flask_1 /ops_venv/bin/python manage.py create-db
docker exec -it naonedia_gunicorn_flask_1 /ops_venv/bin/python manage.py import-data

# Start api-model
docker-compose -f api-model/docker-compose.yml up -d 

# Install pelias CLI
git clone https://github.com/pelias/docker.git ~/pelias
ln -s ~/pelias/pelias /usr/local/bin/pelias

# Create pelias dir
mkdir -p /tmp/pelias/france
chown -R $USER /tmp/pelias 

# Start pelias
pelias compose pull
pelias elastic start
pelias elastic wait
pelias elastic create
pelias download all
pelias prepare all
pelias import all
pelias compose up