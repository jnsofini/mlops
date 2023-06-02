Setup the environment and start a local prefect server via `prefect server start`

In the terminal to run the code run `prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`

To run the code run 

```sh
python 3.4/orchstrate.py
```

## Deployment
We are using a beta feature. Run the following
```sh
prefect project  init
```

The following output is generated

```sh
Created project in /home/fini/Learning/mlops/mlops-zoomcamp/03-orchestration with the following new files:
.prefectignore
deployment.yaml
prefect.yaml
.prefect/
```

To deploy we run 

```sh
prefect deploy 3.4/orchestrate.py:main_flow -n taxi1 -p zoompool
```

and this sends deployment to server. At this point nothing is running, the orchetration is only deployed. To start the pool

```sh
 prefect worker start --pool 'zoompool'
 ```


 After setting this up we encountered an error. However, when we run simply `python 3.4/orchstrate.py` we get the result. After some thoughts the error might be coming because we don not have the data present on github.