import pickle

from flask import Flask, request, jsonify

with open('lin_reg.bin', 'rb') as f_in:
    (dv, model) = pickle.load(f_in)

# Makes sure the data is preprocess in way to conform to what
# the app expects
def prepare_features(ride):
    features = {
    'PU_DO' : '%s_%s'% (ride['PULocationID'], ride['DOLocationID']),
    'trip_distance' : ride['trip_distance']
    }
    return features


def predict(features):
    X = dv.transform(features)
    preds = model.predict(X)
    return float(preds[0])

# Start a flask application to make the script run as flast server
app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json() #Flask function don't take params, they can be gotten from request

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696) # Debugging server only