# Tests

The code here is taken from the streaming service that we containerized.

## Environment

We also need to add py test to the environment

Setting up the environment we run

```sh
cd ../../04-deployment/streaming/
pipenv shell
pipenv install --dev pytest
cd ../../06-best-practices/credit-risk/
```

We have added the _Pipfile_ and _Pipfile.lock_ here for the record.

## Configure VScode to run test

First ensure you have the python extension installed. This helps with discovering of the python environments in the computer. Run _control + shift + p_ and type _python intepreter_ in the search window and select the right environment. This provides us with autocomplete and the ability to check the code of the packages used. Confirm that pytest works by running `pytest` in the terminal and sensuring it is the right one via `which pytest`. The terminal might become very long. In that case if you want to showten it use PS1="> ". Create a diectory called _Tests_ to hold the test cases. To configure pytest, select the _Testing_ icon on the left. It looks like a beaker. Select pytest and confirm the direstory with the test cases, here _tests_.


We noticed that we need `pandas` to run opbinning so we are creating a new environment to work with it.

## Running Tests

We had dificulties at the start when setting tests. So the challenge is that we are reading global variables just vto run a test to prepare features. The test is run from the test discovery. We can however run from the terminal via simple `pytest tests/`


## Test container

we can build the image via 

```sh
docker build -t stream-mode-credit-score:v1 .
# ========
docker run -it --rm \
    -p 8080:8080 \
    -e TEST_RUN="True"
    -e AWS_DEDAULT_REGION="us-west-2 \
    stream-mode-credit-score:v1

```


```sh
export AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)
export REGION=us-west-2

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="1dfce710dc824ecab012f7d910b190f6" \
    -e TEST_RUN="False" \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}\
    -e AWS_DEFAULT_REGION=${REGION} \
    stream-mode-credit-score:v1
```



aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
            "cust": {
                "riskperformance": 0,
                "externalriskestimate": 57,
                "msinceoldesttradeopen": 176,
                "msincemostrecenttradeopen": 4,
                "averageminfile": 87,
                "numsatisfactorytrades": 18,
                "numtrades60ever2derogpubrec": 0,
                "numtrades90ever2derogpubrec": 0,
                "percenttradesneverdelq": 89,
                "msincemostrecentdelq": 2,
                "maxdelq2publicreclast12m": 4,
                "maxdelqever": 6,
                "numtotaltrades": 18,
                "numtradesopeninlast12m": 1,
                "percentinstalltrades": 56,
                "msincemostrecentinqexcl7days": 4,
                "numinqlast6m": 1,
                "numinqlast6mexcl7days": 1,
                "netfractionrevolvingburden": 93,
                "netfractioninstallburden": 72,
                "numrevolvingtradeswbalance": 5,
                "numinstalltradeswbalance": 3,
                "numbank2natltradeswhighutilization": 1,
                "percenttradeswbalance": 100
            },
            "cust_id": 19
        }'


    https://medium.com/@jnsofini/provisioning-basic-infrastructure-in-aws-using-terraform-258f23fb03ca