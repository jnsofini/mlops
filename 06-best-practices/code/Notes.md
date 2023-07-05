
We want to automate everything so we want to use bash. 

Start the bash script with thye _bash shebang_ and also look how to run a command from the script folder, If you search 'run bash script cd to script directory' you can fine something like `cd "$(direname "$0")"`. 

In building the docker image we can always add tags. Git hashes are the best but we don't always commit code. We can use the date. 

```sh
LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
docker build -t ${LOCAL_IMAGE_NAME} .
```

We can build the image with docker via

```sh
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="Test123" \
    -e MODEL_LOCATION="/app/model" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="eu-west-1" \
    -v ${pwd}/model:/app/model \
    stream-model-duration:v2
```

However, it quickly start getting complicated. Let's use docker compose.Use the above info to buiold a docker compose file and run via

```yaml
services:
  backend:
    image: ${LOCAL_IMAGE_NAME}
    ports:
      - "8080:8080"
    environment:
      - PREDICTIONS_STREAM_NAME=${PREDICTIONS_STREAM_NAME}
      - RUN_ID=Test123
      - TEST_RUN=True
      - AWS_DEFAULT_REGION=us-west-2
      - MODEL_LOCATION=/app/model
      - KINESIS_ENDPOINT_URL=http://kinesis:4566/
      - AWS_ACCESS_KEY_ID=abc
      - AWS_SECRET_ACCESS_KEY=xyz
    volumes:
      - "./model:/app/model"
```

```sh
cd integration-test
docker compose up
```

By ensuring that I set TEST_RUN in the docker compose I get and event back.

It is possible for the python tests to fail and yet the shell script returns a non zero status under `echo $?`. We can add `set -e` i.e when you see first non-zero code terminate. This could terminate all the programs, so if we don't desire this, we can write the error code to variable or file. This can be desireable if we want to runn all script. Do this via

```txt
ERROR_CODE=$?`
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
fi
docker-compose down
exit ${ERROR_CODE}
```

We can see the logs and then power down and make a decision on what to do with the sevice. We can look for the error and troubleshoot.

## Kinesis

We will use localstack to test the AWS services locally. We will use docker compose version. There is also a pip install version.

Add it to the docker compose file. We can run the kinesis part only via `docker compose up kinesis`. When it is up and running, check `aws kinesis list-streams`. This one goes to AWS. We can use local stack at 

``` sh
aws --endpoint-url=http://localhost:4566 \
    kinesis list-streams
```

and you can get help via

``` sh
aws --endpoint-url=http://localhost:4566 \
    kinesis --help
```

create stream abd verify via

```bash
aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ride_predictions \
    --shard-count 1
```

To configure our script to accesss this endpoint,
we add environment in docker compose. We run the shell script below

```shell
#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

export PREDICTIONS_STREAM_NAME="ride_predictions"

docker compose up -d

sleep 5

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1

pipenv run python test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker compose logs
    docker compose down
    exit ${ERROR_CODE}
fi


pipenv run python test_kinesis.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    # docker compose down
    # exit ${ERROR_CODE}
fi


# docker compose down

```

we get a response. We need to check that something was indeed stored in kinesis so we start with

### Specifying endpoint URL

```bash
aws --endpoint-url=http://localhost:4566 \
    kinesis list-streams
```

Create kinesis

```bash
aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ride_predictions \
    --shard-count 1
```

Run script  `./run.sh` then check query the shard to get the shard iterator id

```bash
export PREDICTIONS_STREAM_NAME=ride_predictions
aws  --endpoint-url=http://localhost:4566 \
    kinesis     get-shard-iterator \
    --shard-id ${SHARD} \
    --shard-iterator-type TRIM_HORIZON \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --query 'ShardIterator'
```

We use the shard iterator id which we can then used to pull the data as

```sh
aws --endpoint-url=http://localhost:4566  kinesis get-records --shard-iterator "AAAAAAAAAAEutPfVRluXeBaoeNS0ejFo6iyi7xGLCryE1aI3y8At8q+kb/MiOm9JbUupAXB23c5LtueiESDGy/DTbrlr+yEkNeNj2GuOtXtWyQYudNOfQ+TEVd3gE8o4aZkIqmErFVUvI5t2TG7n8ZGR+IbS7S7l7QqeuFoqQMCPh+7wvRn+v/re2rU2DQ6YL1/Pltj8M6asRix4G0xts3zOYVNyY79Z"
```

Next see inside the data by copying the base64 in the "data" key part of the record.

```sh
 echo "eyJtb2RlbCI6ICJyaWRlX2R1cmF0aW9uX3ByZWRpY3Rpb25fbW9kZWwiLCAidmVyc2lvbiI6ICJUZXN0MTIzIiwgInByZWRpY3Rpb24iOiB7InJpZGVfZHVyYXRpb24iOiAyMS4yOTQ1NDUzNDgzMzM0MDgsICJyaWRlX2lkIjogMjU2fX0=" | base64 -d
 ```

 Now, we want to automate everything. We use test_kinesis.py.

 So now we modify the script to run both Kinesis and prediction test. It build services and tear them down when done. So now we have two tests. One in _tests_ and the other in _integration-test_. We can combine them to use `makefile`.


 ## Code Quality

 We will improve the quality of the code via linters. For `pylint` we can run recursively via `pylint --recursive=y .`

 To run `black` start with `black --diff . | less`, once satisfied, run `black .`.