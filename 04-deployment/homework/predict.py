import pickle
import pandas as pd
# import sys
import os

with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)

categorical = ['PULocationID', 'DOLocationID']

def read_data(taxi="yellow", year=2022, month=1):
    filename = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi}_tripdata_{year:04d}-{month:02d}.parquet"
    df = pd.read_parquet(filename)

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


def prediction(data):
    # cols = ['PULocationID', 'DOLocationID', "ride_id"]

    x_val = dv.transform(data[categorical].to_dict(orient='records'))
    y_pred = model.predict(x_val)

    return y_pred

def main():
    year = os.getenv("YEAR", 2022) #sys.argv[1]
    month = os.getenv("MONTH", 2) #sys.argv[2]
    taxi = os.getenv("TAXI", "yellow")
    data = read_data(taxi=taxi, year=int(year), month=int(month))
    
    y_pred = prediction(data)
    import statistics
    print("STD", statistics.stdev(y_pred))
    print("Mean", statistics.mean(y_pred))

if __name__ == "__main__":
    main()
