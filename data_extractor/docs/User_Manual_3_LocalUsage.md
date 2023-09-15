# The OSC Data Extractor User Manual #3
## Usage via local code and local storage

## Foreword

This document tries to explain how to set-up and use the OSC Data Extractor in a fully local
enviroment. In case of 
questions about this documentation contact one of the contributors or set up an issue.

## 1. Prerequisites

You need a Kubernetes environment to work with, which could be Docker Desktop or Podman.

Clone the repository to a local system:

```
git clone https://github.com/os-climate/corporate_data_extraction.git
```

#### 2. Build containers

Now you have create the four docker container:

**Via docker**

```
cd data_extractor/code
docker build --rm -f esg_data_pipeline/Dockerfile -t esg_data_pipeline:latest .
docker build --rm -f model_pipeline/Dockerfile -t model_pipeline:latest .
docker build --rm -f rule_based_pipeline/Dockerfile -t rule_based_pipeline:latest .
docker build --rm -f rule_based_pipeline/Dockerfile -t rule_based_pipeline:latest .
```

**Via podman**

```
cd data_extractor/code
podman build --rm -f esg_data_pipeline/Dockerfile -t esg_data_pipeline:latest .
podman build --rm -f model_pipeline/Dockerfile -t model_pipeline:latest .
podman build --rm -f rule_based_pipeline/Dockerfile -t rule_based_pipeline:latest .
podman build --rm -f coordinator/Dockerfile -t coordinator:latest .
```

#### 3. Run containers:

Next we start the docker with the previously build images.

**Note**: Adjust mounting paths such that /app/ids/corporate_data_extraction/ points to actual 
corporate_data_extraction directory on your platform.

**Via docker**

```
docker run --gpus all -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs esg_data_pipeline:latest 
docker run --gpus all -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs model_pipeline:latest 
docker run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs rule_based_pipeline:latest 
docker run -d -p 2000:2000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs coordinator:latest
```

**Via podman**

```
podman run --privileged -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs esg_data_pipeline:latest 
podman run --privileged -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/models:/app/models -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs model_pipeline:latest 
podman run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs rule_based_pipeline:latest 
podman run -d -p 2000:2000 -v /app/ids/corporate_data_extraction/data_extractor/data:/app/data -v /app/ids/corporate_data_extraction/data_extractor/log:/app/server_logs coordinator:latest
```

## 4. How to use the code?

The code has two functionalities. You can either train/retrain a model or you can start the inference to extract 
data from pdfs (an initial training is needed). We assume the following:
 
* You have already created a new project and if not please see "How to set-up a new project?" section below. 
* The four docker container are created and running and if not please see the previous sections.
* Before making an inference run you need a training run or you have to store a trained model to 
the models folder.

For the following we will call the test project DUMMY.

*Note*: For RB solution, KPI definition is more complex. See the README.md within the rule_based_pipeline folder 
for more information.

If you want to run the training or inference via Python you should log into the coordinator container 
or in any other container/local system which can connect to the three remaining docker. Afterwards you can call one of the 
 following:

```
python3 train_on_pdf.py --project_name=DUMMY --s3_usage=N
python3 infer_on_pdf.py --project_name=DUMMY --s3_usage=N --mode=both 
```

In a local environment you may have to change to the code folder (via "cd data_extractor/code").

s3_usage: Is a boolean to reflect if you use S3 as the data source or not. In a local setup this has to be 'N'.
mode: Is a string which is RB (rule-based only), ML (machine learning only), both, or none (for just doing 
postprocessing).

This will start training or inference by connecting to the three worker docker. 