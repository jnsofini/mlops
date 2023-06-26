import json
# import base64


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    return 10.5


def lambda_handler(event, context):
    print(json.dumps(event))
    
    ride = event['ride']
    ride_id = event['ride_id']

    features = prepare_features(ride)
    prediction = predict(features)

    prediction_event = {
        # 'model': 'ride_duration_prediction_model',
        # 'version': '123',
        'prediction': {
            'ride_duration': prediction,
            'ride_id': ride_id   
        }
    }

    return {
            'ride_duration': prediction,
            'ride_id': ride_id   
        }
    


    # return {
    #     'predictions': predictions_events
    # }

