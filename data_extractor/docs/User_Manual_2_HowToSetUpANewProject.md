# The OSC Data Extractor User Manual #2

## How to set-up a new project?

## Foreword

This document tries to explain how to create a new project either locally or on S3. In case of
questions about this documentation contact one of the contributors or set up an issue.

## 1. Prerequisites

If you want to use S3 then you have to have access to an S3 bucket and
for local creating you should clone the repository to a local folder:

```
git clone https://github.com/os-climate/corporate_data_extraction.git
```

Note: In case you use a cloud based solution where you cloned the repo to you need access to the cloned repo
as well.

To have a better understanding of what kind of structure we create check the example project:

```
corporate_data_extraction/data_extractor/data/TEST
```

### 2. Local data

When using the data next to your code then you have to create the folder structure for a new project in the
data folder. For that you can use the Python File:

```
corporate_data_extraction/data_extractor/code/setup_project.py
```

After creation you have to fill the data folder with the following files:

- kpi_mapping.csv: The questions you want to ask the tool.
- annotations.xlsx: A file containing already training data (which can be empty at the beginning)
- Some pdfs (either in training or inference)
- The settings file: This contains information for the code how you want to run it and maybe has to be adjusted.

```
corporate_data_extraction/data_extractor/data/TEST/settings.yaml
```

- On top you have to load at least one model for the relevance training. For that you can take any model which is
  supported by farm from Hugging Face, for example "roberta-base". The model has to be downloaded and stored in the
  models folder and then to be specified in the settings file.

### 3. Project on S3

If you want use the code on S3 then you have to specify the two buckets where the input/output data (main_bucket)
and the interim files (interim_bucket) should be stored. The global variables which store this information are
defined in the following yaml file in the repository:

```
corporate_data_extraction/data_extractor/data/s3_settings.yaml
```

Whatever setup you are using you additionally have to define the environment variables specified in the yaml
and add the needed secrets and access information there.

On S3 there is no folder system, but names reflect a synthetic "folder structure" and in the following we
will use the folder terminology to clarify what is needed nevertheless. You can use the S3_Connection_Notebook.ipynb
to connect to S3 from a local system via boto to S3.

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

- kpi_mapping.csv: The questions you want to ask the tool.
- annotations.xlsx: A file containing already training data (which can be empty at the beginning)
- Some pdfs (either in training or inference)
- The settings file: This contains information for the code how you want to run it and maybe has to be adjusted.

```
corporate_data_extraction/data_extractor/data/TEST/settings.yaml
```

- On top you have to load at least one model for the relevance training. For that you can take any model which is
  supported by farm from Hugging Face, for example "roberta-base". The model has to be downloaded and stored as a
  .zip file to S3 into the folder. For roberta-base it would be named:

```
corporate_data_extraction/data_extractor/models/RELEVANCE/Text/roberta_base.zip
```
