# Deployment

This directory contain deployment of the credit scoring system. We start with batch deployment. In this form of deployment, we simply read the model and run the deployment. 

## [Batch Deployment](batch)

Here we deloy the model in batch form. This will run periodically, say every month as data comes in and with the ability to run at any time when triggered. The deployment here is orchestrated with `Prefect`. Go to the batch [deployment readme](batch/README.md) to get more details on how this was done.

## [API Webservice Deployment](webservice)

Here we deloy the model as a webservice running a `fastapi` backend packaged into a docker container and deployed in the cloud. in batch form. This model can be executed on demand as it an API however, it should have rate limitation. A batch of data in a json format can be pushed to it and the customer credit scores gotten.  The deployment here is orchestrated with GitHub Actions in a CICD pipeline. Go to the webservice [deployment readme](webservice/README.md) to get more details on how this was done.

## Test

The components and the whole is testes for both deployment.

### Batch deploy tests

### Webservices deployment tests

A docker-compose.yml file was build to deploy the app. The docker deployment is tested with [unit test](test/test_docker.py). The deployment

## Docker build locally
 
Some of the common commands we ran when building are

```sh
docker build -t test-credit-score .
docker run -it --rm -p 8002:8002 test-credit-score 
python test.py # To run the test on the container. Make sure port matches
```

To deploy from a docker compose simply use `docker compose u -d` and `docker compose down` for deployment and tearing down of the app.

The `flyctl` is at `/.fly/bin/flyctl`.
