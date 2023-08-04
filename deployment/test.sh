#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi


echo "Working directory:=== " $PWD

echo "============================================"
echo "Staring the the services via docker compose."
echo "============================================"

docker compose up -d

sleep 5

# pipenv run python test_docker.py
echo "Making a test call to the API."

python test/test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    echo "============================================"
    echo "Error encountered! Logging and tearing down."
    docker compose logs
    docker compose down
    exit ${ERROR_CODE}
fi

echo "============================================"
echo "=======Tearing the sevices down!."==========
echo "============================================"
docker compose down
