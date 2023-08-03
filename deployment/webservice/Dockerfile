FROM tiangolo/uvicorn-gunicorn:python3.11-slim
RUN pip install -U pip && pip install pipenv 
COPY [ "Pipfile", "Pipfile.lock", "./" ]
# We don't need to create a venv, so we use the option --system
#  --deploy ensures that the installation is from an upto date lockfile else error
RUN pipenv install --system --deploy

WORKDIR /app
COPY fastapi-app/ /app/



EXPOSE 8002 

ENTRYPOINT ["uvicorn", "app:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8002"]

