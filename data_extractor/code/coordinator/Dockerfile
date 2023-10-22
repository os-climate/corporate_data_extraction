FROM ubuntu:22.04
SHELL ["/bin/bash", "-c"]

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils wget python3 python3-pip vim

COPY ./code/coordinator/requirements.txt /app/code/requirements.txt
COPY ./code/coordinator/entry.sh /app/code/entry.sh
COPY ./code/coordinator/server_coordinator.py /app/code/server_coordinator.py
COPY ./code/infer_on_pdf.py /app/code/infer_on_pdf.py
COPY ./code/train_on_pdf.py /app/code/train_on_pdf.py
COPY ./code/kpi_mapping.csv /app/code/kpi_mapping.csv
COPY ./code/setup_project.py /app/code/setup_project.py
COPY ./code/utils/config_path.py /app/code/config_path.py
COPY ./code/utils/s3_communication.py /app/code/s3_communication.py
COPY ./data /app/data
COPY ./models /app/models

WORKDIR /app/code

RUN pip install -r requirements.txt

RUN chgrp -R 0 /app/code && chmod -R g=u /app/code
RUN chmod -R a+x /app/code

RUN mkdir -p /app/server_logs

RUN chmod -R 777 /app/server_logs
RUN chmod -R 777 /app/data
RUN chmod -R 777 /app/models

# Adding vs code server
RUN mkdir -p /.vscode-server
RUN mkdir -p /.vscode-remote
RUN chmod -R 777 /.vscode-server
RUN chmod -R 777 /.vscode-remote

CMD ./entry.sh
