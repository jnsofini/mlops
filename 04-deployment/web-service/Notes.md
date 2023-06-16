# Web Server

Here we are provided with a model from previous work.
This model is provided to us by say email. We only know it has a dict vectorizer and a linear regression and that it takes two features _PULocationID and DOLocationID_ that needs to be cocatenated in preprocessing. That is all.

## Setting up venv

Since we had a lock file we run `pipenv install`, followed by `pipenv shell`. The command line  might be too lon. Feel free to use `PS1="> "` to make it shorter.

In flask, we can test by putting the snippet

```python
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696) # Debugging server only
```

at the bottom of the file. A warning will come about production use. This is to conform with security. When we are in production we use

```sh
gunicorn --bind=0.0.0.0:9696 predict:app
```

When this is running we can test by sending a `request` to the sever with some json data. The script `test.py` is meat to do that. Check it by running `python test.py`. Ensure you run in an env with `requests` library.

## Containerizing the app

Once everything is working we can containerize the application. Provided is the docker file which we can use to build a docker image. Am docker image can be optained by running

```sh
docker build -t ride-duration-prediction-service:v1 .
```

Here is the docker file and the explanationns of the varous command

```yaml
# Pulling from the minimal python image slim
FROM python:3.10-slim
# Install or update pip and install pipenv
RUN pip install -U pip && pip install pipenv 
# Specify the working directory from which all commands will be run
WORKDIR /app
# Copy the two files from local to docker
COPY [ "Pipfile", "Pipfile.lock", "./" ]
# Install packages without creating a venv, use --system 
#  --deploy installation is from an uptodate lockfile else throws an error
RUN pipenv install --system --deploy
COPY [ "predict.py", "lin_reg.bin", "./" ]
# Port exposed by flas is available in the system
EXPOSE 9696 
# Starts a server
# Format is file:flask-app, here is predict:app
ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
```

With an image, we can start the app in the server via

```sh
docker run -it --rm -p 9696:9696  ride-duration-prediction-service:v1
```

- `--it` for interactive mode
- `-rm` to remove container when done
- `-p` to publish port as _host-port:container-port_

Things to do at the end

- Remove pipenv environment
