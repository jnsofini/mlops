from time import sleep
from prefect_aws import S3Bucket, AwsCredentials
import settings
from pathlib import Path

def get_config():
    config = settings.load_env_vars(root_dir=Path(__file__).parent)
    return config

def create_aws_creds_block(aws_access_key_id: str, aws_secret_access_key: str):
    my_aws_creds_obj = AwsCredentials(
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key
    )
    my_aws_creds_obj.save(name="my-aws-creds", overwrite=True)


def create_s3_bucket_block(bucket_name = "moose-solutions"):
    aws_creds = AwsCredentials.load("my-aws-creds")
    my_s3_bucket_obj = S3Bucket(
        bucket_name=bucket_name, 
        credentials=aws_creds
    )
    my_s3_bucket_obj.save(name="mlops-s3-block", overwrite=True)


if __name__ == "__main__":
    config = get_config()
    create_aws_creds_block(
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"]
    )
    sleep(5)
    create_s3_bucket_block()
