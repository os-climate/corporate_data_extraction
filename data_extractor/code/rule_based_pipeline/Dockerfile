FROM ubuntu:20.04

LABEL maintainer="ismail.demir@investmentdataservices.com"
LABEL version="1.0"
LABEL description="Image for rule-based solution."

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get update
RUN apt-get install -y python3 python3-pip wget gfortran libopenblas-dev liblapack-dev libpng-dev libfreetype-dev libfontconfig

COPY ./rule_based_pipeline /app/code/rule_based_pipeline

RUN chgrp -R 0 /app/code/rule_based_pipeline && chmod g=u /app/code/rule_based_pipeline
RUN chmod -R a+x /app/code/rule_based_pipeline

WORKDIR /app/code/rule_based_pipeline

RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1+1_ppa0_eoan_amd64.deb
RUN pip install -e .
RUN mkdir -p /app/server_logs
RUN chmod -R 777 /app/server_logs

#USER 1234

CMD ./entry.sh
