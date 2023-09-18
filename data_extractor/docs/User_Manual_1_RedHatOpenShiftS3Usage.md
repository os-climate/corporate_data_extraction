# The OSC Data Extractor User Manual #1
## Usage via UI RedHat Open Shift with S3 data storage

## Foreword

This document tries to explain how to set-up and use the OSC Data Extractor with the RedHat Open Shift 
user interface in connection with the Amazon S3 data storage. In case of 
questions about this documentation contact one of the contributors or set up an issue.

## 1. Prerequisites

This guide is written for the UI of Red Hat OpenShift Platform version 4.10 with
Kubernetes version v1.23.17+16bcd69 in combination with data storage to Amazon S3.

To set up and run the projects on Red Hat OpenShift Platform, you need:

An account at a Red Hat OpenShift cluster with sufficient privilege to +add Git repositories. This typically
will include the privileges to create Deployments, Pods, Secrets, DeploymentConfigs, PersistentVolumeClaims, 
(optionally) Services and (optionally) Routes.

Two S3 buckets to load and store the data. One for the input and output data (here and in the following
called s3-landing-bucket) and one for the interim data (here and in the following
called s3-interim-bucket).

A project on S3 was already created. If not check the User_Manual on "How to set up a new project?".

### 2. RedHat Open Shift Set Up

This part will explain you how you configure the system on RedHat Open Shift. If this is already configured
just jump to the next section.

#### 2.1. Environment variables:

For the connection to S3 you will need the following environment variables

| Name | Value (resource) | Value(key) |
| -----| ---------------- | ---------- |
|LANDING_AWS_ACCESS_KEY | s3-landing-bucket | AWS_ACCESS_KEY|
|LANDING_AWS_BUCKET_NAME | s3-landing-bucket | AWS_BUCKET_NAME|
|LANDING_AWS_ENDPOINT | s3-landing-bucket | AWS_ENDPOINT|
|LANDING_AWS_SECRET_KEY | s3-landing-bucket | AWS_SECRET_KEY|
|INTERIM_AWS_ACCESS_KEY | s3-interim-bucket | AWS_ACCESS_KEY|
|INTERIM_AWS_BUCKET_NAME | s3-interim-bucket | AWS_BUCKET_NAME|
|INTERIM_AWS_SECRET_KEY | s3-interim-bucket | AWS_SECRET_KEY|
|INTERIM_AWS_ENDPOINT | s3-interim-bucket | AWS_ENDPOINT|

You can create environment variables via "Secrets" tab in the "Developer" mode. 
They will be assigned once you have a deployment.

#### 2.2 PVC Creation

Additionally, you will need storage for **each** POD. For that you have to switch to "Administrator" 
mode or contact your admin to create under "Storage" PVC (PersistentVolumeClaims). This storage will be assigned 
once you have a deployment.
In total you will set up four deployments and depending on how many pods you want to have you need 4*#PODS PVC's.   

#### 2.3 Create Deployments 

First choose in Developer mode (at the upper left corner) the "+Add" and then choose "Import from Git". 

#### 2.3.1. Extraction Docker

##### Docker File

For the extraction docker you need the following details:

```
Git Repo URL: https://github.com/os-climate/corporate_data_extraction.git
Git reference: main 
Context dir: /data_extractor/code
Source Secrete: os-climate-github-pat (only in OSC environment accessible)
Dockerfile path: esg_data_pipepline/Dockerfile
```

**NOTE**: Do not create a route to the application (only for the coordinator this needs to be done if you want to 
have access from outside).

##### Global Variables

Now you have to add the global variables via the drop down menu. 

*Note*: You could also add later the environment variables as follows
 to your deployment YAML file: 
```
    spec:
          ...
          containers:
              -   name: ...
                  image: ...      
                  env:
                    - name: LANDING_AWS_ACCESS_KEY
                      valueFrom:
                        secretKeyRef:
                          name: s3-landing-bucket
                          key: AWS_ACCESS_KEY
                    - name: LANDING_AWS_BUCKET_NAME
                      valueFrom:
                        secretKeyRef:
                          name: s3-landing-bucket
                          key: AWS_BUCKET_NAME
                    - name: LANDING_AWS_ENDPOINT
                      valueFrom:
                        secretKeyRef:
                          name: s3-landing-bucket
                          key: AWS_ENDPOINT
                    - name: LANDING_AWS_SECRET_KEY
                      valueFrom:
                        secretKeyRef:
                          name: s3-landing-bucket
                          key: AWS_SECRET_KEY
                    - name: INTERIM_AWS_ACCESS_KEY
                      valueFrom:
                        secretKeyRef:
                          name: s3-interim-bucket
                          key: AWS_ACCESS_KEY
                    - name: INTERIM_AWS_BUCKET_NAME
                      valueFrom:
                        secretKeyRef:
                          name: s3-interim-bucket
                          key: AWS_BUCKET_NAME
                    - name: INTERIM_AWS_SECRET_KEY
                      valueFrom:
                        secretKeyRef:
                          name: s3-interim-bucket
                          key: AWS_SECRET_KEY
                    - name: INTERIM_AWS_ENDPOINT
                      valueFrom:
                        secretKeyRef:
                          name: s3-interim-bucket
                          key: AWS_ENDPOINT

```

##### Advanced options

For the extraction docker you have to set the Target Port to be **4000**.

#### 2.3.2 Model Docker

##### Docker File

For the model docker you need the following details:

```
Git Repo URL: https://github.com/os-climate/corporate_data_extraction.git
Git reference: main 
Context dir: /data_extractor/code
Source Secrete: os-climate-github-pat (only in OSC environment accessible)
Dockerfile path: model_pipeline/Dockerfile
```

**NOTE**: Do not create a route to the application (only for the coordinator this needs to be done if you want to 
have access from outside).

##### Global Variables

See 2.3.1. Extraction Docker -- Global variables

##### Advanced options

For the model docker you have to set the Target Port to be **6000**.

#### 2.3.3 Rule Based Docker

##### Docker File

For the model docker you need the following details:

```
Git Repo URL: https://github.com/os-climate/corporate_data_extraction.git
Git reference: main 
Context dir: /data_extractor/code
Source Secrete: os-climate-github-pat (only in OSC environment accessible)
Dockerfile path: rule_based_pipeline/Dockerfile
```

**NOTE**: Do not create a route to the application (only for the coordinator this needs to be done if you want to 
have access from outside).

##### Global Variables

See 2.3.1. Extraction Docker -- Global variables

##### Advanced options

For the rule based docker you have to set the Target Port to be **8000**.

#### 2.3.4 Coordinator Docker

##### Docker File

For the model docker you need the following details:

```
Git Repo URL: https://github.com/os-climate/corporate_data_extraction.git
Git reference: main 
Context dir: /data_extractor/code
Source Secrete: os-climate-github-pat (only in OSC environment accessible)
Dockerfile path: rule_based_pipeline/Dockerfile
```

**NOTE**: For this docker you might want to create a route to the application as this docker has only two possible ways
to communicate (see section 1.2).

##### Global Variables

See 2.3.1. Extraction Docker -- Global variables

##### Advanced options

For the coordinator docker you have to set the Target Port to be **2000**.

#### 2.4 GPU 

If you want a GPU machine (only needed for model docker) then you have to modify the model_docker by adding a 
toleration and a NodeSelector which states that gpu should be present:

```
      nodeSelector:
        nvidia.com/gpu.present: 'true'

      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
        - key: odh/notebook
          value: 'true'
          effect: NoSchedule
``` 

## 3. How to use the code?

The code has two functionalities. You can either train/retrain a model or you can start the inference to extract 
data from pdfs (an initial training is needed). We assume the following:
 
* The four docker container are created and running and if not see the sections
before.
* Before making an inference run you need a training run or you have to store a trained model to 
the models folder.

For the following we will call the test project DUMMY (this is a prerequisite to have a project (see above)).

*Note*: For RB solution, KPI definition is more complex. See the README.md within the rule_based_pipeline folder 
for more information.

### 3.1. Using the code via Python

If you want to run the training or inference via Python you should log into the coordinator container. One way
of achieving this is:

1) Go to Developer mode
2) Open Topology
3) Click on the coordinator deployment
4) Click on the connect pod
5) Open the terminal tab
 
Afterwards you can call one of the following:

```
python3 train_on_pdf.py --project_name=DUMMY --s3_usage=Y
python3 infer_on_pdf.py --project_name=DUMMY --s3_usage=Y --mode=both 
```

s3_usage: Is a boolean to reflect if you use S3 as the data source or not, which is in this set-up mandatory to
be 'Y'
mode: Is a string which is RB (rule-based only), ML (machine learning only), both, or none (for just doing 
postprocessing).

This will start training or inference by connecting to the three worker docker. 

### 3.2. Using the code via services or routes

If you have configured a service or a route to the coordinator you can for example call it via the request package
in python.

**Service**

For a service inside of a container in the namespace you can do:

```
import requests
http_string= http://192.0.2.0:2000/train?project_name=DUMMY&s3_usage=Y
tmp = requests.get(http_string)
http_string_2= http://192.0.2.0:2000/infer?project_name=DUMMY&s3_usage=Y&mode=both
tmp_2 = requests.get(http_string_2)
```

*Note*: Here the IP address is of course a synthetic one and has to be replaced by the correct one.

**Route**

For a route from the outside world you could call the environment by any browser for example like so:

```
http://example.com/train?project_name=DUMMY&s3_usage=Y
http://example.com/infer?project_name=DUMMY&s3_usage=Y&mode=both 
```

Currently the server is not giving you any response and so you can only see logs when logging into the 
dockers or by waiting until a final result is available.

