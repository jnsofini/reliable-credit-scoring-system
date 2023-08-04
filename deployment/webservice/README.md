# Cloud Deployment

Here we deploy the model to the cloud. The choice of cloud is the [fly.io](https://fly.io). Their free tier offer a generous package for us to play around with out model. Read more about [deploying models](https://fly.io/docs/flyctl/deploy/#options) and [deploying python apps](https://fly.io/docs/languages-and-frameworks/python/) in fly.io.

## Setting Up

We started by creating a free account and installing the fly.io cli as specified in the website. We installed here and didn't add to Path so it is located in `~/.fly/bin/flyctl`. As a result we can get help via `~/.fly/bin/flyctl --help`. We started by using an app pakages in a docker container. This done via the following steps ran from the project root

- Login via `~/.fly/bin/flyctl auth login`. A prompt will as you to login via UI or grant permission if you were already logged in.
- Start the config via `~/.fly/bin/flyctl launch`. It will as for informations like

```sh
    It asked me to
    add name
    select region
    database, redis etc
    added .dockerignore
    added fly.io
```

You will see the following _Then imaged started building_. The app was created and deployed. The image of the app is also sent to a registry and the info displayed in the terminal [`image`](registry.fly.io/credit-scoring). The app is located in this [link](https://credit-scoring.fly.dev/docs).

## Deployment via GitHub Actions

We want to shift focus and implement a continuos deployment (CD) of our app via GitHub Actions. [As explained in the fly.io page](https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/), we need to set credentials, a configuration file `fly.toml` on the basic. Additional information is located [here](https://dev.to/ruthmoog/deploying-a-project-to-flyio-with-github-actions-2c7e).

Typically, `fly.toml` should not be sent to to public repository as it contains a lot of information about the app. We can guard it just like a terraform state file if we must have a public repo.

The GitHub Action to deploy the API to the cloud is presented in the [`.github/workflow/fly.yml`](.github/workflows/fly.yml). There are three parts of the Action which includes:

- Build a docker image
- Push the image to Docker Hub
- Deploy image to fly.io

Once we push code to banch `deploy/fly` it automatically build the image and push to Docker Hub, and then pull it and deploy in fly.io.