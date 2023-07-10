FROM public.ecr.aws/lambda/python:3.10

RUN pip install -U pip
RUN pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy
# Copying model as we haven't figured a way to read it.
# COPY [ "model/model.pkl", "./" ]
COPY model model
COPY ["config.py", "model.py", "./" ]

COPY ["lambda_function.py", "./" ]

CMD [ "lambda_function.lambda_handler" ]
