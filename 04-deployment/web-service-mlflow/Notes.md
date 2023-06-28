# Web Service with model registry

We want to use the previous code with best practices. Previously, we said if we have been emailed a model, we can still deploy it. Here we want to have access to the experiments that generated the model in a way cross functional teams work. The model developers are there and the engineers to deploy and scale are also access the model from a cenntral registry.

## Set up

We start by setting the virtual environment as explained [web service section](../web-service/Notes.md). We also formatted the scripts by refactoring. To make the terminal show we ran again `PS1="> "`.

We started the sevice in the same way as in web service section and ran the test tp get a predict.

## Preparing the service

In preparing the sevice, we decided to access the model using the run ID. This way we can load it from the artifact store, without reference to the mlflow server. This is a mechanism of decoupling the storage backend from the UI service. That way, the server could be down but we still access the models. So we avoided the boiler plate version of loading model and artifact shown below

```python
mlflow.set_experiment("---")
MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
RUN_ID = "1dfce710dc824ecab012f7d910b190f6"
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
path = mlflow.artifacts.download_artifacts(run_id=RUN_ID, path='dict_vectorizer')
with open(path, "rb") as f:
    dv = pickle.loaf(f)

logged_model = f"runs:/{RUN_ID}/models"
# Alternative using stage: logged_model = f"models:/{experiment-name}/{stage}
model = mlflow.pyfunc.load_model(logged_model)
#
```

This was avoided by using scikit-learn pipeline to package the model and dict vectorizer as a single object. Another avoidance is using the _stage_ which is stored in the data base and thus access via the server.

Basically, we saw how to

- Remove model depences on tracking server
- Simply the loading of model and sartifact
