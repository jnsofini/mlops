
<!-- ```sh
pipenv install
pipenv shell
pipenv install 
pipenv install notebook pandas pyarrow scikit-learn fastparquet prefect
pipenv install --dev mlflow isort black autopep8 pytest seaborn matplotlib hyperopt optuna pylint
``` -->

The environment for this homework was set via the following commands run one at a time

```sh
pipenv install #Create venv
pipenv shell #acticate env
pipenv install scikit-learn==1.2.2 pandas==2.0.2 pyarro

```

The _predict.py_ was prepared to accept environment variables. The docker image was modified just like we did in other lessons. The mage was build from the file and ran as a container via

```sh
docker build -t homework4 . #Create image
docker run --rm -it homework4 # Run image as container
```

The entry point was `bash` and the evironment variable was set as `export MONTH=2` while keeping year and taxi unchanged. The script was run on the root as `python predict.py` to get the results printed. All the commands as follows

```sh
export MONTH=2 # Set env variable
python predict.py # Run python script
```
