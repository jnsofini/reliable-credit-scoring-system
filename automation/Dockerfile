FROM public.ecr.aws/lambda/python:3.10

RUN pip install -U pip && pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy
# Copying model as we haven't figured a way to read it.
# COPY [ "model/model.pkl", "./" ]
# COPY model model
COPY ["lambda_function.py", "config.py", "model.py", "./" ]

CMD [ "lambda_function.lambda_handler" ]
