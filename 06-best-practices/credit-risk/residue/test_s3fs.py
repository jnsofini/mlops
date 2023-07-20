# import pickle

# import pandas as pd
# from s3fs.core import S3FileSystem


# def load_model(run_id='dev'):
#     s3_file = S3FileSystem()

#     model = pickle.load(
#         s3_file.open("s3://moose-solutions-mlops-registry/scorecards/dev/model.pkl")
#     )
#     return model


# model = load_model()
# val_data = pd.read_parquet(
#     "/home/fini/github-projects/mlops/capstone/credit-risk-model/data/X_val.parquet"
# )
# print(model.score(val_data))

# Boto3 version
# ====================================
import pickle
import boto3
import boto3.session
import pandas as pd

# cred = boto3.Session().get_credentials()
# ACCESS_KEY = cred.access_key
# SECRET_KEY = cred.secret_key
# SESSION_TOKEN = cred.token  ## optional

s3client = boto3.client('s3', 
                        # aws_access_key_id = ACCESS_KEY, 
                        # aws_secret_access_key = SECRET_KEY, 
                        # aws_session_token = SESSION_TOKEN
                       )

response = s3client.get_object(
    Bucket='moose-solutions-mlops-registry', 
    Key='scorecards/dev/model.pkl'
    )

body = response['Body'].read()
model = pickle.loads(body)

val_data = pd.read_parquet(
    "/home/fini/github-projects/mlops/capstone/credit-risk-model/data/X_val.parquet"
)
print("=============================")
print(model.score(val_data))
print("=============================")