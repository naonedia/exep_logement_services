#!/usr/bin/env bash
source TAG.sh

wget -q https://download.geofabrik.de/europe/france/pays-de-la-loire-latest.osm.pbf -O osm/pays-de-la-loire-latest.osm.pbf

docker-compose build

docker-compose up -d

docker exec -it naonedia_openpoi_db_1 /ops_venv/bin/python manage.py create-db
docker exec -it naonedia_gunicorn_flask_1 /ops_venv/bin/python manage.py import-data