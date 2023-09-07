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
```

*Note*: The coordinator docker is missing here.

**via podman**

```
podman run --privileged -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs esg_data_pipeline:latest 
podman run --privileged -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs model_pipeline:latest 
podman run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs rule_based_pipeline:latest 
```

*Note*: The coordinator docker is missing here.

### 3.2. RedHat Open Shift Set Up

T.B.D.
