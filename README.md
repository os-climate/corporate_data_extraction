# corporate_data_extraction

# 1. Build containers:

cd code
docker build --rm -f esg_data_pipeline/Dockerfile -t esg_data_pipeline:latest .
docker build --rm -f model_pipeline/Dockerfile -t model_pipeline:latest .
docker build --rm -f rule_based_pipeline/Dockerfile -t rule_based_pipeline:latest .

# 2. Run containers:

Note: Adjust mounting paths such that /app/ids/corporate_data_extraction/ points to actual corporate_data_extraction directory on your platform.

2.1 via docker
docker run --gpus all -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data:/app/data -v /app/ids/corporate_data_extraction/models:/app/models -v /app/ids/corporate_data_extraction/log:/app/server_logs esg_data_pipeline:latest 
docker run --gpus all -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data:/app/data -v /app/ids/corporate_data_extraction/models:/app/models -v /app/ids/corporate_data_extraction/log:/app/server_logs model_pipeline:latest 
docker run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data:/app/data -v /app/ids/corporate_data_extraction/log:/app/server_logs rule_based_pipeline:latest 

2.2 via podman
podman run --privileged -d -p 4000:4000 -v /app/ids/corporate_data_extraction/data:/app/data -v /app/ids/corporate_data_extraction/models:/app/models -v /app/ids/corporate_data_extraction/log:/app/server_logs esg_data_pipeline:latest 
podman run --privileged -d -p 6000:6000 -v /app/ids/corporate_data_extraction/data:/app/data -v /app/ids/corporate_data_extraction/models:/app/models -v /app/ids/corporate_data_extraction/log:/app/server_logs model_pipeline:latest 
podman run -d -p 8000:8000 -v /app/ids/corporate_data_extraction/data:/app/data -v /app/ids/corporate_data_extraction/log:/app/server_logs rule_based_pipeline:latest 

# 3. Setup new project

Note: You might instead use already included project "ESG" as example.

cd code
python setup_project.py


# 4. Training (skip if you only want to use RB solution)

cd code
python train_on_pdf.py


# 5. Inference

cd code
python infer_on_pdf.py

Note: You may use parameter --mode with argument: RB=rule based only, ML=machine learning only, both=both solutions (default), non = only joining output (helpful for debugging)
Note: For RB solution, KPI defintion is more complex. See the README.md within the rule_based_pipeline folder for more information.
