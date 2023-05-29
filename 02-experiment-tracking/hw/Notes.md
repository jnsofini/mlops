# Notes

Notes on Assignments. We started by serring an environment variable in the linux terminal with _TAXI_DATA_FOLDER=path/to/folder/_. The command to run the preprocessing is

``` bash
python preprocess_data.py --raw_data_path $TAXI_DATA_FOLDER --dest_path ./output
```

and that to check the size is `ls -lthr output`

Next, launch MLflow server via

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db \
--default-artifact-root ./artifacts_store
```