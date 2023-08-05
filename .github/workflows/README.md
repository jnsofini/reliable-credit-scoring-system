# GitHub Actions

In this directory, we have many GitHub Actions. These actions are perform Continuous Integration and Continous Delivery CICD.

The actions perform the following jobs

## [Continuous test](ci-tests.yml)

Unit test and integration test of the python code. The infrastructure as code is also tested and validated at this stage. If any of this fails the deployment won't work take place

## [Continuous deployment of streaming services](cd-deploy.yml)

The infrastructure is provisioned. The docker images are build and pushed to ECR and then the lambda function starts with a dummy image that is updated when the ECR stage is completed.

## [Coninuous Deployment of API](fly.yml)

This action builds a docker image and push to DockerHub. The image is deployed as an API in the cloud.