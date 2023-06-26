import json

data = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49641667361005213384739839176645187418587579714681962498",
                "data": "Hellothisisatest",
                "approximateArrivalTimestamp": 1686632116.285,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49641667361005213384739839176645187418587579714681962498",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::410605826834:role/lambda-kinesis-role",
            "awsRegion": "us-west-2",
            "eventSourceARN": "arn:aws:kinesis:us-west-2:XXXX:stream/score_events",
        }
    ]
}

print(json.dumps(data))
