#!/bin/bash

date_time=$(date +'%d_%h_%Y:%H_%M')
log_file_path="/app/server_logs/coordinator_logs_${date_time}.txt"
cd /app/code
python3 server_coordinator.py > $log_file_path 2>&1 &

sleep infinity