# exep_logement_services
Hosts different services used for creating models. We use docker technology.

## Dataset
 We retrieved the dataset [here](https://download.geofabrik.de/europe/france/pays-de-la-loire.html)
 It's often updated, if you want to stay up-to-date, you might want to re-download it.

 After downloading it you need to place 2 copies inside the following folders :
 * openpoiservice/osm/
 * openrouteservice/docker/data/

## Docker

Install docker from [here](https://docs.docker.com/install/)

After installing it you need to run the following command

```shell
cd openpoiservice/docker
docker-compose up -d
# The container name should be 'openpoiservice_gunicorn_flask_1' if not replace the name below by yours
docker exec -it openpoiservice_gunicorn_flask_1 /ops_venv/bin/python manage.py create-db
docker exec -it openpoiservice_gunicorn_flask_1 /ops_venv/bin/python manage.py import-data
```

```shell
cd openrouteservice/docker
docker-compose up -d
```

## After

 Now you are ready to use both api  
 open route service will serve its API to http://localhost:9090/ors  
 open POI service will serve its API to http://localhost:5000  

 We used [openrouteservice-py](https://github.com/GIScience/openrouteservice-py). It allowed us to enhance our dataset with points of interest around houses.