# Experiment Tracking
Experiment tracking is the process of keeping track of all the relevant information from an ML experiment, which includes:

- Source code
- Environment
- Data
- Model
- Hyperparameters
- Metrics

It sets out to solve the challenges with reproducibility, organization and optimization.

The following concepts will be treated here here.

- ML experiment: the process of building an ML model
- Experiment run: each trial in an ML experiment
- Run artifact: any file that is associated with an ML run
- Experiment metadata: information about an ML experiment like the source code used, the name of the user,

We use MLflow to achive this. It provides:

- Tracking
- Models
- Model registry
- Projects

An experiment is basically a model run. Some of the items we will track include:

- Paremeters
- Metrics
- Metadata
- Artifacts
- Models

To run with a data base do we import MLflow and set sqlite backend. Without specifying an srtifact store, MLflow will create a dir call `mlruns` in the local.

conda activate mlops, run the following

``` bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

In this case, the artifacts are stored in a directory called _mlruns_. This is the default name given to the artifact backend. You can add one by using

``` bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts_store
```

Some times vscode crashes and MLflow is running in the background. To kill it
`ps -A | grep gunicorn` and then `kill pid`

When we have one data scientist working on a model that won't be deployed, MLflow is note necessary. However, in a cross functional team with one data scientist, we might need MLflow, however, it can be in a local server. In the case where multiple data scientists are building a model in a cross functional team that involves deployment, we need a remote server.

In this case we need to configire

- Backend store for file e.g local filesystem or SQLAlchemy compatible
- Artifact store eg local or remote like S3
- Treacking server, none, localhost or remote


## Implementation

Here we have setup an mlflow server in AWS with a postgres backend deployed in RDS. The artifact store is configure to use S3.



## Data Versioning
Now that we have gone through a basic notebook work in chapter 1, we will try to start improving things gradually. One of them is versioning the data. In this case we will use `DVC`. 