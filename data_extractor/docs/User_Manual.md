# The OSC Data Extractor User Manual

## Foreword

This document tries to explain how to set-up and use the OSC Data Extractor. In case of 
questions about this documentation contact one of the contributors or set up an issue.


## 1. How to use the code?

The code has two functionalities. You can either train/retrain a model or you can start the inference to extract 
data from pdfs (an initial training is needed). We assume the following:
 
* You have already created a new project and if not please see "How to set-up a new project?" section below. 
* The four docker container are created and running and if not please see "How to set up the containers?" section
below.
* Before making an inference run you need a training run or you have to store a trained model to 
the models folder.

For the following we will call the test project DUMMY.

*Note*: For RB solution, KPI defintion is more complex. See the README.md within the rule_based_pipeline folder 
for more information.

### 1.1. Using the code via Python

If you want to run the training or inference via Python you should log into the coordinator container 
or in any other container/local system which can connect to the three remaining docker. Afterwards you can call one of the 
 following:

```
python3 train_on_pdf.py --project_name=DUMMY --s3_usage=Y
python3 infer_on_pdf.py --project_name=DUMMY --s3_usage=Y --mode=both 
```

In a local environment you may have to change to the code folder (via "cd code").

s3_usage: Is a boolean to reflect if you use S3 as the data source or not
mode: Is a string which is RB (rule-based only), ML (machine learning only), both, or none (for just doing 
postprocessing).

This will start training or inference by connecting to the three worker docker. 

### 1.2. Using the code via services or routes

If you have configured a service or a route to the coordinator you can for example call it via the request package
in python.

**Service**

For a service inside of a namespace you can do:

```
import requests
http_string= http://172.40.103.147:2000/train?project_name=DUMMY&s3_usage=Y
tmp = requests.get(http_string)
http_string_2= http://172.40.103.147:2000/infer?project_name=DUMMY&s3_usage=Y&mode=both
tmp_2 = requests.get(http_string_2)
```

*Note*: Here the IP address is of course a synthetic one and has to be replaced by the correct one.

**Route**

For a route from the outside world you could call the environment by any browser for example like so:

```
http://not_existing_page.org/train?project_name=DUMMY&s3_usage=Y
http://not_existing_page.org/infer?project_name=DUMMY&s3_usage=Y&mode=both 
```

Currently the server is not giving you any response and so you can only see logs when logging into the 
dockers or by waiting until a final result is available.

## 2. How to set-up a new project?

The following part explains how you can set up a new project.

### 2.1. Local data

When using the data next to your code then you have to create the folder structure for a new project in the 
data folder. For that you can use the Python File:

```
corporate_data_extraction/data_extractor/code/setup_project.py
```

Afterwards, you have to fill the data folder with the following files:

* kpi_mapping.csv
* annotations.xlsx
* Some pdfs (either in training or inference)
* The settings file maybe has to be adjusted.

```
corporate_data_extraction/data_extractor/data/TEST/settings.yaml
```

On to you have to load at least one model for the relevance training. For that you can take any model which is
supported by farm from Hugging Face, for example "roberta-base". The model has to be downloaded and stored in the
models folder and then to be specified in the settings file.

### 2.2. Data on S3

If you want use the code on S3 then you have to specify the two buckets where the input/output data (main_bucket) 
and the interim files (interim_bucket) should be stored. The global variables which store this information are
defined in the following yaml file in the repository:

```
corporate_data_extraction/data_extractor/data/s3_settings.yaml
```

Whatever setup you are using you additionally have to define the environment variables specified in the yaml
and add the needed secrets and access information there.

On S3 there is no folder system, but names reflect a synthetic "folder structure" and in the following we
will use the folder terminology to clarify what is needed nevertheless. 

For a new project you will then need to set up the following folder structure (here for the test project with name
DUMMY):

```
DUMMY/
|-- data/
|   |-- input/
|       |-- kpi_mapping
|       |-- annotations
|       |-- pdfs
|           |-- training
|           |-- inference
|   |-- interim/
|   |-- output/
|-- models/
```

So, when the prefix is "corporate_data_extraction_projects" then a pdf "Test.pdf" in the "input folder" would be

```
corporate_data_extraction_projects/DUMMY/data/input/pdfs/inference/Test.pdf
```

The needed files in the input folder are 

* kpi_mapping.csv
* annotations.xlsx
* Some pdfs (either in training or inference)
* The settings file (corporate_data_extraction_projects/DUMMY/data/settings.yaml) where an example can be found in 
the repository under 
```
corporate_data_extraction/data_extractor/data/TEST/settings.yaml
```
* At least a model for the relevance training has to be stored on S3. For that you can take any model which is
supported by farm from Hugging Face, for example "roberta-base". The model has to be downloaded and stored as a 
.zip file to S3 into the folder
```
corporate_data_extraction/data_extractor/models/RELEVANCE/Text/roberta_base.zip
```

## 3. "How to set up the containers?"

### 3.1. Local Set Up

#### 3.1.1. Build containers

```
cd code
docker build --rm -f esg_data_pipeline/Dockerfile -t esg_data_pipeline:latest .
docker build --rm -f model_pipeline/Dockerfile -t model_pipeline:latest .
docker build --rm -f rule_based_pipeline/Dockerfile -t rule_based_pipeline:latest .
```

#### 3.1.2. Run containers:

Note: Adjust mounting paths such that /app/ids/corporate_data_extraction/ points to actual 
corporate_data_extraction directory on your platform.

**via docker**

```
docker run --gpus all -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs esg_data_pipeline:latest 
docker run --gpus all -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs model_pipeline:latest 
docker run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs rule_based_pipeline:latest 
docker run -d -p 2000:2000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs coordinator:latest
```

**via podman**

```
podman run --privileged -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs esg_data_pipeline:latest 
podman run --privileged -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs model_pipeline:latest 
podman run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs rule_based_pipeline:latest 
podman run -d -p 2000:2000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs coordinator:latest
```

### 3.2. RedHat Open Shift Set Up

#### 3.2.1. Environment variables:

For the connection to S3 you will need the following environment variables

| Name | Value (resource) | Value(key) |
| -----| ---------------- | ---------- |
| LANDING_AWS_ACCESS_KEY | s3-landing-bucket | AWS_ACCESS_KEY|
|LANDING_AWS_BUCKET_NAME | s3-landing-bucket | AWS_BUCKET_NAME|
|LANDING_AWS_ENDPOINT | s3-landing-bucket | AWS_ENDPOINT|
|LANDING_AWS_SECRET_KEY | s3-landing-bucket | AWS_SECRET_KEY|
|INTERIM_AWS_ACCESS_KEY | s3-interim-bucket | AWS_ACCESS_KEY|
|INTERIM_AWS_BUCKET_NAME | s3-interim-bucket | AWS_BUCKET_NAME|
|INTERIM_AWS_SECRET_KEY | s3-interim-bucket | AWS_SECRET_KEY|
|INTERIM_AWS_ENDPOINT | s3-interim-bucket | AWS_ENDPOINT|

You can create environment variables via "Secrets" tab in the "Developer" mode. They will be assigned once you
have a deployment.

#### 3.2.2 PVC Creation

Additionally, you will need storage for **each** POD. For that you have to switch to "Administrator" mode or contact your
admin to create under "Storage" PVC (PersistentVolumeClaims). This storage will be assigned once you have a deployment.
In total you will set up four deployments and depending on how many pods you want to have you need 4*#PODS PVC's.   

#### 3.2.3 Create Deployments 

First choose in Developer mode (at the upper left corner) the "+Add" and then choose "Import from Git". 

#### 3.2.3.1. Extraction Docker

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

#### 3.2.3.2 Model Docker

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

See 3.2.3.1. Extraction Docker -- Global variables

##### Advanced options

For the model docker you have to set the Target Port to be **6000**.

#### 3.2.3.3 Rule Based Docker

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

See 3.2.3.1. Extraction Docker -- Global variables

##### Advanced options

For the rule based docker you have to set the Target Port to be **8000**.

#### 3.2.3.4 Coordinator Docker

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

See 3.2.3.1. Extraction Docker -- Global variables

##### Advanced options

For the coordinator docker you have to set the Target Port to be **2000**.

#### 3.2.4 GPU 

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