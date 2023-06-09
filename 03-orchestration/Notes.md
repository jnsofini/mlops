# Setup the environment

To get started we can start a __local prefect server__ via

```sh
prefect server start
```

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

 if you had not created this process workpool you could use

 ```sh
 prefect worker start --pool 'zoompool' -t process
 ```

 After setting this up we encountered an error. However, when we run simply `python 3.4/orchstrate.py` we get the result. After some thoughts the error might be coming because we don not have the data present on github.

 In trying to run this from the browser, it fails. Best guess is that the default branch is main. Let's check that.

 Let's first check by trying to deploy from a deployment.yaml

```sh
 prefect deploy --all
 ```

 Finally nothing worked. So I went started trying to just ensure it can see the code. I decided to move the `prefect init` command to the root, so that i set everything in the root directory. The code worked, however, it encountered an error when it tried to get the data as I didn't store my data on github. So I decided to try with setting the data to be read from a url instead. Eveything worked well! Takeaways: For now, since I don't know how to set the working directory, I will do everything from the root.

 The deployment and running from browser was

 ```sh
 prefect deploy 03-orchestration/3.4/orchestrate.py:main_flow -n taxi3 -p zoompool
 prefect worker start --pool 'zoompool'
 ```

 With it working I sample the data and stored in S3. The created a deployment for both local and s3.


 Now running `prefect deploy --all` and then `prefect deployment run main-flow-s3/nyc_taxi_s3_data` t run fdeomloyment from terminal. I arrive at at a pending flow if i run `prefect worker start --pool 'mlops'` it starts to run. Simply because we have to start the work pool as well. So we could do these the other way around.

 If I run the command

 ```sh
 prefect deployment run main-flow-s3/nyc_taxi_s3_data
 ```
  it creates a flow which is just ready to be triggered. I can trigger from ui or  by running

```sh
prefect worker start --pool 'mlops'
```

We can set parameters by selecting custom rum on the UI. That way you can change the inputs to the functions. Also we can set the schedule time ffrom the deployment UI as well. We can equally set the interval (in seconds) from terminal via

 ```sh
 prefect deployment set-schedule main-flow-s3/nyc_taxi_s3_data --interval 120
 ```

 To change profile I used `prefect profile create dev` and to  with `prefect profile ls` you see default and dev. To select dev `prefect proforile use dev` and with login, it takes you to the prefect cloud as this is a cloud base account.  Navigating to the root and running `prefect deploy --all`, the two deployments are deloyed to prefect cloud. The I created a process `prefect worker start -p mlops -t process` and could trigger it from the cloud UI. Next I set some automation where I created an even to sent an email when task completes. There are multiple options to take from including flow entering _pending, failed_ etc.

 Another way to see details is via `prefect version`


 Setting up a profile called _local_

 ```sh
 prefect profile create local
 prefect profile use local
 prefect config set PREFECT_API_URL='http://127.0.0.1:4200/api'
 ```

 ## Automated Notification

Prefect offers several [automation recipies](https://docs.prefect.io/2.10.12/cloud/automations/) for workflows.
It’s often helpful to be notified when something with your dataflow doesn’t work
as planned. Let's create an email notification for to use with your own Prefect server instance.
In your virtual environment, install the prefect-email integration with 

```bash
pip install prefect-email
```

Make sure you are connected to a running Prefect server instance through your
Prefect profile.
See the docs if needed: https://docs.prefect.io/latest/concepts/settings/#configuration-profiles

To register the new block with your server 
 - Notifications 
 - Select the state of choice
 