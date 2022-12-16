#!/bin/bash

date_time=$(date +'%d_%h_%Y:%H_%M')
log_file_path="/app/server_logs/rule_based_logs_${date_time}.txt"
cd /app/code/rule_based_pipeline/rule_based_pipeline
python3 rb_server.py > $log_file_path 2>&1 &

sleep infinity
