#!/usr/bin/env bash

# Build api-model image
cd api-model
./push.sh

# Build OpenPOIService
cd ../openpoiservice
./push.sh

# Build OpenRouteService
cd ../openrouteservice/docker
./push.sh
