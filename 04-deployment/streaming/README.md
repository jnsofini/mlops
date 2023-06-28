## Machine Learning for Streaming

* Scenario
* Creating the role 
* Create a Lambda function, test it
* Create a Kinesis stream
* Connect the function to the stream
* Send the records 

Links

* [Tutorial: Using Amazon Lambda with Amazon Kinesis](https://docs.amazonaws.cn/en_us/lambda/latest/dg/with-kinesis-example.html)

## Code snippets

### Sending data

When they are in the same region

```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --stream-name $KINESIS_STREAM_INPUT \
    --partition-key 1 \
    --data "Hello, this is a test."
```

When they are in diferent regions

```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --region us-east-2 #specify region
    --stream-name $KINESIS_STREAM_INPUT \
    --partition-key 1 \
    --data "Hello, this is a test."
```

Decoding base64

```python
base64.b64decode(data_encoded).decode('utf-8')
```

Record example

```json
{
    "ride": {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }, 
    "ride_id": 123
}
```

Sending this record

```bash
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66
        }, 
        "ride_id": 156
    }'
```

### Test event


```json
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49630081666084879290581185630324770398608704880802529282",
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1654161514.132
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49630081666084879290581185630324770398608704880802529282",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::XXXXXXXXX:role/lambda-kinesis-role",
            "awsRegion": "eu-west-1",
            "eventSourceARN": "arn:aws:kinesis:eu-west-1:XXXXXXXXX:stream/ride_events"
        }
    ]
}

{
  "Records": [
    {
      "kinesis": {
        "kinesisSchemaVersion": "1.0",
        "partitionKey": "1",
        "sequenceNumber": "49641667361005213384739839176645187418587579714681962498",
        "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ==",
        "approximateArrivalTimestamp": 1686632116.285
      },
      "eventSource": "aws:kinesis",
      "eventVersion": "1.0",
      "eventID": "shardId-000000000000:49641667361005213384739839176645187418587579714681962498",
      "eventName": "aws:kinesis:record",
      "invokeIdentityArn": "arn:aws:iam::XXXXXXXXXX:role/lambda-kinesis-role",
      "awsRegion": "us-west-2",
      "eventSourceARN": "arn:aws:kinesis:us-west-2:XXXXXXXXXX:stream/ride_events"
    }
  ]
}
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq
``` 


### Running the test

```bash
export PREDICTIONS_STREAM_NAME="ride_predictions"
export RUN_ID="1dfce710dc824ecab012f7d910b190f6"
export TEST_RUN="True"

python test-start.py
```

You will see the prediction
`[{'model': 'ride_duration_prediction_model', 'version': '123', 'prediction': {'ride_duration': 18.321633541366506, 'ride_id': 156}}]`

Lets see what is in the stream

### Putting everything to Docker where we build and then run the container

```bash
docker build -t stream-model-duration:v1 .
```

We might neet to fix credentials. The way I did this was to set them as environment variables in Linux as clearly explained [here.](https://cameroneckelberry.co/words/getting-aws-credentials-into-a-docker-container-without-hardcoding-it). That is because I use a profile and also dislike copying credentials. Note that, my profile is default. You can change to your profile to the corresponding profile. Alternatively, follow [this link.](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html). You can select commands for the OS that match your system.

```sh
export AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)
export REGION=us-west-2

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="1dfce710dc824ecab012f7d910b190f6" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}\
    -e AWS_DEFAULT_REGION=${REGION} \
    stream-model-duration:v1
```

URL for testing:

* http://localhost:8080/2015-03-31/functions/function/invocations



### Configuring AWS CLI to run in Docker

To use AWS CLI, you may need to set the env variables:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="1dfce710dc824ecab012f7d910b190f6" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    stream-model-duration:v1
```

Alternatively, you can mount the `.aws` folder with your credentials to the `.aws` folder in the container:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e1efc53e9bd149078b0c12aeaa6365df" \
    -e TEST_RUN="True" \
    -v ~/.aws:/root/.aws \
    stream-model-duration:v1
```

### Publishing Docker images

Creating an ECR repo

```bash
aws ecr create-repository --repository-name duration-model
```

With that I get the output

```json
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-west-2:XXXXXXX:repository/duration-model",
        "registryId": "410605826834",
        "repositoryName": "duration-model",
        "repositoryUri": "XXXXXXX.dkr.ecr.us-west-2.amazonaws.com/duration-model",
        "createdAt": "2023-06-13T11:00:15-06:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}
```

Logging in get region from the ecr

```bash
# aws ecr get-login-password
ECR_REGION=us-west-2
aws ecr get-login-password \
--region ${ECR_REGION} \
| docker login \
--username AWS \
--password-stdin 410605826834.dkr.ecr.${ECR_REGION}.amazonaws.com
```

When I ran the above command I encountered an error with login. _Error saving credentials: error storing credentials - err: exit status 1, out: `error storing credentials - err: exit status 1, out: `pass not initialized: exit status 1: Error: password store is empty. Try "pass init".``_ I seached online and used [this thread](https://stackoverflow.com/questions/71770693/error-saving-credentials-error-storing-credentials-err-exit-status-1-out) to resolve it by running. This might be the [link](https://docs.docker.com/desktop/get-started/#credentials-management-for-linux-users) to follow or [this](https://docs.docker.com/desktop/get-started/).

```sh
service docker stop
rm ~/.docker/config.json
service docker start
```

Re-running the command I get a login success. The I rebuild the image and pushed again.

Pushing to ECR we take local image and tag to ECR command to ask it to transfer the image.

```bash
REMOTE_URI="410605826834.dkr.ecr.us-west-2.amazonaws.com/duration-model"
REMOTE_TAG="v1"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="stream-model-duration:v1"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```

The image is deployed to ECR.

Create new lambda with container source and add link. Add environment variables `PREDICTIONS_STREAM_NAME="ride_predictions" RUN_ID="1dfce710dc824ecab012f7d910b190f6"`. 


We also needed to give the lambda function permission to access our artifact store in s3. The permission looks like



Also had to update the lambda function as it was timing out. Added memory to 256MB and the execution time to 30s. Now if we send logs via

```sh
aws kinesis put-record     --stream-name ${KINESIS_STREAM_INPUT}     --partition-key 1  --cli-binary-format raw-in-base64-out    --data '{
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 30.5
        }, 
        "ride_id": 156
    }'
```

we can see the output. Sadly we didn't do enough logging so we don't see much that is familiar to us. Now we can play around with this by reading from the stream as follows

```sh
KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)
```

Manipulating the RESULT via