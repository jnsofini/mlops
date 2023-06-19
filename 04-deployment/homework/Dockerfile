FROM svizor/zoomcamp-model:mlops-3.10.0-slim
RUN pip install -U pip && pip install pipenv 
WORKDIR /app
COPY [ "Pipfile", "Pipfile.lock", "./" ]
RUN pipenv install --system --deploy

COPY [ "predict.py" , "./"]
ENTRYPOINT [ "/bin/bash" ]
    