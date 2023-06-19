"""
In this script, we place services that we need to prepare ourself to run a prediction. 
This includes sevices to load model and to prepare data for the scripts that runs the predictions.
"""

import os
import mlflow

BUCKET = os.getenv('BUCKET', "moose-solutions-mlops-registry" )
RUN_ID = os.getenv('RUN_ID', "1dfce710dc824ecab012f7d910b190f6")
EXPERIMENT_ID = os.getenv('RUN_ID', 1)

def load_model():
    """Loads model from an S3 artifact store.

    Creates a path to the model using bucket name, experiment id and run id.

    Returns:
        _type_: _description_
    """
    logged_model = f's3://{BUCKET}/{EXPERIMENT_ID}/{RUN_ID}/artifacts/model'
    # logged_model = f'runs:/{RUN_ID}/model'
    model = mlflow.pyfunc.load_model(logged_model)
    return model

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

