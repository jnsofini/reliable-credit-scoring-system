
# Monitoring example

## Prerequisites

You need following tools installed:

- `docker`
- `docker-compose` (included to Docker Desktop for Mac and Docker Desktop for Windows )

## Preparation

Note: all actions expected to be executed in repo folder.

- Create virtual environment and activate it (eg. `python -m venv venv && source ./venv/bin/activate` or `conda create -n venv python=3.11 && conda activate venv`)
- Install required packages `pip install -r requirements.txt`
- Run `baseline_model_nyc_taxi_data.ipynb` for downloading datasets, training model and creating reference dataset

## Monitoring Example

### Starting services

To start all required services, execute:

```bash
docker-compose up
```

It will start following services:

- `db` - PostgreSQL, for storing metrics data
- `adminer` - database management tool
- `grafana` - Visual dashboarding tool

### Sending data

To calculate evidently metrics with prefect and send them to database, execute:

```bash
python evidently_metrics_calculation.py
```

This script will simulate batch monitoring. Every 10 secinds it will collect data for a daily batch, cacluate metrics and insert them into database. This metrics will be avaliable in Grafana in preconfigured dashboard.

### Accsess dashboard

- In your browser go to a `localhost:3000`
The default username and password are `admin`

- Then navigate to `General/Home` menu and click on `Home`.

- In the folder `General` you will see `New Dashboard`. Click on it to access preconfigured dashboard.

### Ad-hoc debugging

Run `debugging_nyc_taxi_data.ipynb` to see how you can perform a debugging with help of Evidently `TestSuites` and `Reports`

### Stopping services

To stop all services, execute:

```bash
docker-compose down
```


### Variables

To [export variables](https://stackoverflow.com/questions/19331497/set-environment-variables-from-file-of-key-value-pairs) in a config.env file while ignoring comments starting with # we run `export $(grep -v '^#' config.env | xargs)`. And if you want to unset all of the variables defined in the file, use this: `unset $(grep -v '^#' .env | sed -E 's/(.*)=.*/\1/' | xargs)`

### Running servcies

To start the service run

```sh
 docker compose --env-file config/config.env up -d
```

To stop the services run

```sh
docker compose --env-file config/config.env down
```
