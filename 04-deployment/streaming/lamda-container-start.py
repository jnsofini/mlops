import os
import json
import boto3
import base64
import mlflow

kinesis_client = boto3.client('kinesis')
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')

# model
BUCKET = "mlops-registry"
RUN_ID = os.getenv(
    'RUN_ID', 
    "1dfce710dc824ecab012f7d910b190f6"
    )
EXPERIMENT_ID = os.getenv('EXPERIMENT_ID', 1)

logged_model = f's3://{BUCKET}/{EXPERIMENT_ID}/{RUN_ID}/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
print(logged_model)
model = mlflow.pyfunc.load_model(logged_model)

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    return 10


def lambda_handler(event, context):
    # print(json.dumps(event))
    
    predictions_events = []
    
    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        ride_event = json.loads(decoded_data)

        # print(ride_event)
        ride = ride_event['ride']
        ride_id = ride_event['ride_id']
    
        features = prepare_features(ride)
        prediction = predict(features)
    
        prediction_event = {
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': prediction,
                'ride_id': ride_id   
            }
        }
        
        predictions_events.append(prediction_event)

    # send recodes to another stream
            # if not TEST_RUN:
        kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
            )
        
        predictions_events.append(prediction_event)

    # For testing only
    return {
        'predictions': predictions_events
    }

