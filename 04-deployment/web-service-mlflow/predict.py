import os
import pickle

import mlflow
from flask import Flask, request, jsonify


BUCKET = "moose-solutions-mlops-registry"
RUN_ID = os.getenv(
    'RUN_ID', 
    "1dfce710dc824ecab012f7d910b190f6"
    )
EXPERIMENT_ID = os.getenv('RUN_ID', 1)

logged_model = f's3://{BUCKET}/{EXPERIMENT_ID}/{RUN_ID}/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
