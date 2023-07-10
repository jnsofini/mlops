# Scoring Service.

Here the code refactoring started and is working at this stage.

For some reason the service is working after extensive trial. Not entirely sure what happened of what changed. But here is the command to build and run the service

```sh
docker build -t stream-mode-credit-score:v1 .

export AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)

docker run -it --rm     -p 8080:8080     -e PREDICTIONS_STREAM_NAME="ride_predictions"     -e RUN_ID="1dfce710dc824ecab012f7d910b190f6"     -e TEST_RUN="True"     -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}     -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}    -e AWS_DEFAULT_REGION=${REGION}     stream-mode-credit-score:v1


```

We can add model location, and then do best practice of not copying the model and instead mount the volume

docker run -it --rm     -p 8080:8080     -e PREDICTIONS_STREAM_NAME="ride_predictions"     -e RUN_ID="1dfce710dc824ecab012f7d910b190f6"     -e TEST_RUN="True"     -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}     -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}    -e AWS_DEFAULT_REGION=${REGION}     stream-mode-credit-score:v2


```sh
docker build -t stream-mode-credit-score:v2 .

export AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)

docker run -it --rm     -p 8080:8080     -e PREDICTIONS_STREAM_NAME="ride_predictions"     -e RUN_ID="t234"     -e TEST_RUN="True"     -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}     -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}    -e AWS_DEFAULT_REGION=${REGION} -e MODEL_LOCAITON="/app/model" -e MODEL_TYPE="optbin" -v ${PWD}/models:/app/model    stream-mo
de-credit-score:v2
```

when I don't copy the model inside it doesnt down

Finally we did

docker build -t stream-mode-credit-score:v2 .

and 

```sh
docker run -it --rm     -p 8080:8080     -e PREDICTIONS_STREAM_NAME="ride_predictions"     -e RUN_ID="1dfce710dc824ecab012f7d910b190f6"     -e TEST_RUN="True"     -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}     -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}    -e AWS_DEFAULT_REGION=${REGION} -v ${PWD}/model:/model     stream-mode-credit-score:v2
```


Lastly use these to go to docker compose.

docker run -it --rm     -p 8080:8080     -e PREDICTIONS_STREAM_NAME="ride_predictions"     -e RUN_ID="1hshs"     -e TEST_RUN="True"     -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}     -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}    -e AWS_DEFAULT_REGION=${REGION} -v ${PWD}/model:/model -e MODEL_LOCATION=/model    stream-mode-credit-score:v2


We created the docker compose by translating the long docker command. Various environment variables are added. Everything worked. 



## Code Quality

__pylint__: 