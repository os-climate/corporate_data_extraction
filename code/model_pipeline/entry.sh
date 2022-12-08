#!/bin/bash


date_time=$(date +'%d_%h_%Y:%H_%M')
log_file_path="/app/server_logs/model_pipeline_logs_${date_time}.txt"
cd /app/code/model_pipeline/model_pipeline
python3 inference_server.py > $log_file_path 2>&1 &



#cd /model_pipeline/notebooks
#jupyter notebook --ip=0.0.0.0 --port=8889 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

sleep infinity