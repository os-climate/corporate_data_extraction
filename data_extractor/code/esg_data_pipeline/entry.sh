#!/bin/bash

date_time=$(date +'%d_%h_%Y:%H_%M')
log_file_path="/app/server_logs/extractions_logs_${date_time}.txt"
cd /app/code/esg_data_pipeline/esg_data_pipeline
python3 extraction_server.py > $log_file_path 2>&1 &

#cd /esg_data_pipeline/notebooks
#jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

sleep infinity
