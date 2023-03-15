FROM ubuntu:20.04

#ENV http_proxy="http://proxy-ids-poc-d.we1.azure.aztec.cloud.allianz:80"
#ENV https_proxy="http://proxy-ids-poc-d.we1.azure.aztec.cloud.allianz:80"

LABEL maintainer="ismail.demir@investmentdataservices.com"
LABEL version="1.0"
LABEL description="Image for rule-based solution."

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y software-properties-common
#RUN add-apt-repository -E --yes ppa:linuxuprising/libpng12
RUN apt-get update
#RUN apt-get install -y python3 python3-pip gfortran libopenblas-dev liblapack-dev libpng-dev libfreetype-dev libpng12-0 libfontconfig
RUN apt-get install -y python3 python3-pip gfortran libopenblas-dev liblapack-dev libpng-dev libfreetype-dev libfontconfig

COPY ./rule_based_pipeline /app/code/rule_based_pipeline

RUN useradd -ms /bin/bash admin
RUN chown admin:admin /app/code/rule_based_pipeline/rule_based_pipeline/pdftohtml_mod/pdftohtml_mod
RUN chgrp -R 0 /app/code/rule_based_pipeline/rule_based_pipeline/pdftohtml_mod/pdftohtml_mod && \
    chmod -R g=u /app/code/rule_based_pipeline/rule_based_pipeline/pdftohtml_mod/pdftohtml_mod
    
RUN chmod u+x /app/code/rule_based_pipeline/rule_based_pipeline/pdftohtml_mod/pdftohtml_mod

#WORKDIR /app/code/rule_based_pipeline
#RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1+1_ppa0_eoan_amd64.deb
#RUN pip install -e .

#RUN mkdir -p /app/server_logs

#RUN chmod u+x entry.sh
#CMD ./entry.sh
CMD sleep infinity
