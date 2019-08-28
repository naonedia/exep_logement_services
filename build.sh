#!/usr/bin/env bash

# Build api-model image
cd api-model
./build.sh

# Build OpenPOIService
cd ../openpoiservice
./build.sh

# Build OpenRouteService
cd ../openrouteservice/docker
./build.sh

# Build api-model image
cd ../../api-model
./build.sh