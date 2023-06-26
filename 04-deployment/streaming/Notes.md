# Setup up

We did the following

- Created a lambda version of the predict
- deploy it
- create kinesis stream
- push data to stream
- get lambda to read the data

## Without Kinesis

Steps 1,2. Put the function in _lamnda-start-no-stream.py_ in the lambda. Create test called _test1_ with values

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

The following should be returned.

```txt
Test Event Name
test-1

Response
{
  "ride_duration": 10.5,
  "ride_id": 123
}

Function Logs
START RequestId: 232845a9-6b8e-44c0-b05a-4b9d1f9e5522 Version: $LATEST
{"ride": {"PULocationID": 130, "DOLocationID": 205, "trip_distance": 3.66}, "ride_id": 123}
END RequestId: 232845a9-6b8e-44c0-b05a-4b9d1f9e5522
REPORT RequestId: 232845a9-6b8e-44c0-b05a-4b9d1f9e5522 Duration: 1.38 ms Billed Duration: 2 ms Memory Size: 128 MB Max Memory Used: 36 MB Init Duration: 109.74 ms

Request ID
232845a9-6b8e-44c0-b05a-4b9d1f9e5522
```

## With Kinesis and No model

Created iam role and policy. See details below. Create kinesis name _ride_events_.
Send a test events to the stream via

```bash
KINESIS_STREAM_INPUT=ride_events
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

Here is the putput

```json
{
    "ShardId": "shardId-000000000000",
    "SequenceNumber": "49641780686612885777013334990893567317652527046950125570"
}
```

Goto lambda function and select Monitor and select view logs in cloudwatch. You see the following.

```json
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49641780686612885777013334990895985169291817671792263170",
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDE1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1686949874.47
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49641780686612885777013334990895985169291817671792263170",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::XXXX:role/lambda-kinesis-role",
            "awsRegion": "us-west-2",
            "eventSourceARN": "arn:aws:kinesis:us-west-2:XXXX:stream/ride_events"
        }
    ]
}

```

We need to use this event with a lambda function. We first parse it and then run predict. In this case we use _lambda-start.py_ with the event above added to a new test called _test-stream_. The followins id the output from the lambda function.

```txt
Test Event Name
test-stream

Response
{
  "predictions": [
    {
      "model": "ride_duration_prediction_model",
      "version": "123",
      "prediction": {
        "ride_duration": 10,
        "ride_id": 156
      }
    }
  ]
}

Function Logs
START RequestId: c4965889-dc0e-4050-9687-2e78a04164dc Version: $LATEST
END RequestId: c4965889-dc0e-4050-9687-2e78a04164dc
REPORT RequestId: c4965889-dc0e-4050-9687-2e78a04164dc Duration: 1.32 ms Billed Duration: 2 ms Memory Size: 128 MB Max Memory Used: 53 MB Init Duration: 283.73 ms

Request ID
c4965889-dc0e-4050-9687-2e78a04164dc
```

## Sending results to another stream

Here we are printing the results of a lambda function. What we want to do is to not have a client server achitecture, but rather sending the predictions to another data stream. We achieve this by

- creating another stream called _ride_predictions_.
- adding role for this to write to that stream

We will use the script _ambda-start-2-streams.py_. The role needs to be updated. So we create another set of permission in a policy to allow sending events to the stream. Replace the lambda with the code above and rerun test-stream. The output is

```txt
Test Event Name
test-stream

Response
{
  "predictions": [
    {
      "model": "ride_duration_prediction_model",
      "version": "123",
      "prediction": {
        "ride_duration": 10,
        "ride_id": 156
      }
    },
    {
      "model": "ride_duration_prediction_model",
      "version": "123",
      "prediction": {
        "ride_duration": 10,
        "ride_id": 156
      }
    }
  ]
}

Function Logs
START RequestId: aad14e58-37d8-4aa2-afab-df24de5619af Version: $LATEST
END RequestId: aad14e58-37d8-4aa2-afab-df24de5619af
REPORT RequestId: aad14e58-37d8-4aa2-afab-df24de5619af Duration: 238.20 ms Billed Duration: 239 ms Memory Size: 128 MB Max Memory Used: 67 MB Init Duration: 378.68 ms

Request ID
aad14e58-37d8-4aa2-afab-df24de5619af
```

How do we verify that the event was sent to that stream? We can used the code snipet shown below to read from stream.

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
```

Explore the results stored in _RESULT_ as shown below. First with `echo $RESULT` I get

```json
{
  "Records": [
    {
      "SequenceNumber": "49641781627525927193417386578568592677232383929922617346",
      "ApproximateArrivalTimestamp": "2023-06-16T15:42:00.470000-06:00",
      "Data": "eyJtb2RlbCI6ICJyaWRlX2R1cmF0aW9uX3ByZWRpY3Rpb25fbW9kZWwiLCAidmVyc2lvbiI6ICIxMjMiLCAicHJlZGljdGlvbiI6IHsicmlkZV9kdXJhdGlvbiI6IDEwLCAicmlkZV9pZCI6IDE1Nn19",
      "PartitionKey": "156"
    }
  ],
  "NextShardIterator": "AAAAAAAAAAFF3MQ8xtDiOGfzQRwVCcT7irYbYgi7MHFJzaH8pC8+QmxhxLBShwM4NmtlZO0VNSVSHNgs8VUhqOYqShXyQ0z9RXH/9ScuCowm9gxBOxG8QBs3xddyNgzeHVm6d/yTQ2mXsd9fKQS5ryDv40P+CrsH/An6jQXph1Ky08Mr2bCGq9WmLxBA4/Z56zD8/unclxIT2BtcnqxAz6M+k/eOHkGZcYeWGLebxH8bA3NIMDLWYQ==",
  "MillisBehindLatest": 0
}
```

Exploring with jq tool we see

```sh
echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq
#out
{
  "model": "ride_duration_prediction_model",
  "version": "123",
  "prediction": {
    "ride_duration": 10,
    "ride_id": 156
  }
}
```

## Adding model

we use script _predict.py_. Test is _test-2-serv.._. Run via

```bash
export PREDICTIONS_STREAM_NAME="ride_predictions"
export RUN_ID="1dfce710dc824ecab012f7d910b190f6"
export TEST_RUN="True"

python  test-2-service-container-start.py
```

You will see the prediction
`[{'model': 'ride_duration_prediction_model', 'version': '123', 'prediction': {'ride_duration': 18.321633541366506, 'ride_id': 156}}]`

Lets see what is in the stream

To see the output, we need to read from the ride_prediction stream again as follows

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
echo ${RESULT} | jq 
```

Output is

```sh
{
  "Records": [
    {
      "SequenceNumber": "49641781627525927193417386578568592677232383929922617346",
      "ApproximateArrivalTimestamp": "2023-06-16T15:42:00.470000-06:00",
      "Data": "eyJtb2RlbCI6ICJyaWRlX2R1cmF0aW9uX3ByZWRpY3Rpb25fbW9kZWwiLCAidmVyc2lvbiI6ICIxMjMiLCAicHJlZGljdGlvbiI6IHsicmlkZV9kdXJhdGlvbiI6IDEwLCAicmlkZV9pZCI6IDE1Nn19",
      "PartitionKey": "156"
    },
    {
      "SequenceNumber": "49641781627525927193417386578569801603052112289831321602",
      "ApproximateArrivalTimestamp": "2023-06-16T16:09:34.918000-06:00",
      "Data": "eyJtb2RlbCI6ICJyaWRlX2R1cmF0aW9uX3ByZWRpY3Rpb25fbW9kZWwiLCAidmVyc2lvbiI6ICIxMjMiLCAicHJlZGljdGlvbiI6IHsicmlkZV9kdXJhdGlvbiI6IDE4LjMyMTYzMzU0MTM2NjUsICJyaWRlX2lkIjogMTU2fX0=",
      "PartitionKey": "156"
    }
  ],
  "NextShardIterator": "AAAAAAAAAAGv52f4B8JSsWwoSfWtoRKpoN5QILRKxcOtfwxNV1CHJGsKzk5gAcCr6bTj7tt7xKt3YvI8masv0+DAj6S9c55fm2aymCJ1KDW3D3HN1iZ6LsuKHxdskyJzzaahakN0H+VO0h+3Yqr7UH05M0UrQ0x7es9w5n4JSq5pmBod1JYerE4qYqUpK8p6dqxU4xAtB3nyI4qT6O5RRABRNKk4X+Te0011UtzbdEBV1sah5iGrFQ==",
  "MillisBehindLatest": 0
}

```

This time we see multiple events showing that the events are present there. This means it is working correctly.

## Lambda in docker container processing streams and pushing to stream

Here, we want to dockerize the lambda function. The dockerfile is provided in the directory.
The explanation is just the same like in the dockerfile in [web-service](../web-service/Dockerfile). The major change is in the command `CMD [ "predict.lambda_handler" ]` which is expressed as `programfile.lambda_handler` where lambda_handler is the name of the main function in aws lambda. With that we can build a docker image via

```bash
docker build -t stream-model-duration:v1 .
```

With the image build, it is time to run a container.
We might neet to fix credentials. The way I did this was to set them as environment variables in Linux as clearly explained [here.](https://cameroneckelberry.co/words/getting-aws-credentials-into-a-docker-container-without-hardcoding-it). That is because I use a profile and also dislike copying credentials. Note that, my profile is default. You can change to your profile to the corresponding profile. Alternatively, follow [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html). You can select commands for the OS that match your system.

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

To test, we can use the same event above that was used to test the lambda outside docker. It is added to the `test_docker.py` already. The URL for testing:
__<http://localhost:8080/2015-03-31/functions/function/invocations>__.  Invoking the the test via `python test_docker.py` on event1 we get

```sh
python test_docker.py 
{
    "predictions": [
        {
            "model": "ride_duration_prediction_model",
            "version": "123",
            "prediction": {
                "ride_duration": 18.321633541366502,
                "ride_id": 256
            }
        }
    ]
}
```

and with event we get

```json
{
    "predictions": [
        {
            "model": "ride_duration_prediction_model",
            "version": "123",
            "prediction": {
                "ride_duration": 18.321633541366506,
                "ride_id": 156
            }
        }
    ]
}
```

 which is the same thing we got on the lambda function. We can then package the function and deploy.

## Deployment

We will send the model to AWS ECR. We can do it via uploading through the console or commandline. Let's use the command line.

```bash
aws ecr create-repository --repository-name duration-model
```

The following is returned

```json
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-west-2:XXXX:repository/duration-model",
        "registryId": "XXXX",
        "repositoryName": "duration-model",
        "repositoryUri": "XXXX.dkr.ecr.us-west-2.amazonaws.com/duration-model",
        "createdAt": "2023-06-16T21:37:39-06:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
:...skipping...
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-west-2:XXXX:repository/duration-model",
        "registryId": "XXXX",
        "repositoryName": "duration-model",
        "repositoryUri": "XXXX.dkr.ecr.us-west-2.amazonaws.com/duration-model",
        "createdAt": "2023-06-16T21:37:39-06:00",
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

We use the URI to send the docker image.

```bash
REMOTE_URI="XXXX.dkr.ecr.us-west-2.amazonaws.com/duration-model"
REMOTE_TAG="v1"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="stream-model-duration:v1"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```

Authentication might fail. If this happens, login to docker. See Readme file for steps to follow. With the code pushed to remote we can create a lambda function from container and deploy it withe triggers as done previously. We can now send a stream. Let's send the following

```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 25
        }, 
        "ride_id": 100
    }'
```

Nothing worked. So we want to deploy a new function and test via old data give in data_docker.json. It timedout and we will add the lambda time. We changed the time out to 30 s a the memory to 256. The following response was gotten

```txt
Executing function: succeeded (logs 
)
Details
The area below shows the last 4 KB of the execution log.
{
  "predictions": [
    {
      "model": "ride_duration_prediction_model",
      "version": "123",
      "prediction": {
        "ride_duration": 18.321633541366506,
        "ride_id": 156
      }
    }
  ]
}
Summary
Code SHA-256
5b989f68ee5386b5ada58f86e8753d4f0d06b041d9dedf1e65df928032e9e3e4
Request ID
00844b54-ce58-472f-97f1-6e53373ff302
Duration
20565.62 ms
Billed duration
20566 ms
Resources configured
256 MB
Max memory used
178 MB
Log output
```

The we ran with two records again. we got the following

```json
{
  "predictions": [
    {
      "model": "ride_duration_prediction_model",
      "version": "123",
      "prediction": {
        "ride_duration": 18.321633541366506,
        "ride_id": 156
      }
    },
```

We can now test via a two way by sending stream to stream _ride_event_ and lambda will process and send to _ride_predictions_. Here is what we sent

```sh
aws kinesis put-record     --stream-name ${KINESIS_STREAM_INPUT}     --partition-key 1     --cli-binary-format raw-in-base64-out     --data '{
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 25
        }, 
        "ride_id": 100
    }'
{
    "ShardId": "shardId-000000000000",
    "SequenceNumber": "49641788553958979895441628980982578375619600118689300482"
}
```

If we go to the monitor and view logs in cloudtrail we can search to see

```list
[{'model': 'ride_duration_prediction_model', 'version': '123', 'prediction': {'ride_duration': 44.46109015964011, 'ride_id': 100}}]

```

We can confirm that such a stream was pushed to _ride_predictions_ as done earlier via

KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT2=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq

## what is here?

```bash
KINESIS_STREAM_INPUT=ride_events
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

## With Kinesis

We needed to understand the data structure we get back from kinesis. This is important as we have to pass the predict params to the lambda function.

We create a producer. This producer will produce data that the lambda function uses. We call it _ride_events_.
We need a role for the lambda to access the kineses. One such role is the _AWSLambdaKinesisExecutionRole_ with the following permission

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:DescribeStream",
                "kinesis:DescribeStreamSummary",
                "kinesis:GetRecords",
                "kinesis:GetShardIterator",
                "kinesis:ListShards",
                "kinesis:ListStreams",
                "kinesis:SubscribeToShard",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

Next step, add role name e.g lambda-kinesis-role.

Next we create a function called _ride_duration_prediction_

Test what streams set we execute

```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --region us-east-2 #specify region
    --stream-name $KINESIS_STREAM_INPUT \
    --partition-key 1 \
    --data "Hello, this is a test."
```

and gets

{
    "ShardId": "shardId-000000000000",
    "SequenceNumber": "49641657104803293599712133856595873235696294845090889730"
}

We want to send the results to another stream. Basically, the lambda function gets results from one stream and runs the prediction and then sends the results to another stream. We call this _ride_predictions_. We need a role for the lambda function to access this stream. We will make this one restrictive. The code used to send data to the consumer is as follows

```python
kinesis_client = boto3.client('kinesis')
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')
...
kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
            )
```

The policy created and added to the role is

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "kinesis:PutRecord",
                "kinesis:PutRecords"
            ],
            "Resource": "arn:aws:kinesis:us-west-2:XXXXXXXX:stream/ride_predictions"
        }
    ]
}
```

It will be good to check that we can read from the stream. See Readme.

Now we can move the code from lambda-start.py in addition to the lines above and combine to give our final code by adding how to get model from mlflow.
