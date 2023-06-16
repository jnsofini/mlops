FROM python:3.10-slim
RUN pip install -U pip && pip install pipenv 
WORKDIR /app
COPY [ "Pipfile", "Pipfile.lock", "./" ]
# We don't need to create a venv, so we use the option --system
#  --deploy ensures that the installation is from an upto date lockfile else error
RUN pipenv install --system --deploy
COPY [ "predict.py", "lin_reg.bin", "./" ]
# Port exposed by flas is available in the system
EXPOSE 9696 
# Format is file:flask-app, here is predict:app
ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]