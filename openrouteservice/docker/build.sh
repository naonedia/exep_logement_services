#!/usr/bin/env bash
source TAG.sh

wget -q https://download.geofabrik.de/europe/france/pays-de-la-loire-latest.osm.pbf -O data/pays-de-la-loire-latest.osm.pbf

docker-compose build