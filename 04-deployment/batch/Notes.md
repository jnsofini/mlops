# Notes

The script is gotten from the _.ipynb_ via `jupyter nbconvert --to script score.ipynb`.

The data source paths were updated to ensure data is pulled from the correct location. We also modified the file to push data to a designated S3 bucket. The file was

Started by starting a prefect server `prefect server start`

After starting the server , I had to run `prefect agent start ml` to start an agent that could run the process.
Found out that the process failed if for the previous month data. This is because the data is not available.

With _score.py_ working we want to perform a model back fill where we retrouspectively apply the model. In this case we call it _score_backfill.py_.
