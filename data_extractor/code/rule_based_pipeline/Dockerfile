FROM ubuntu:20.04

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

# https://stackoverflow.com/questions/58473832/how-do-i-change-the-permissions-in-openshift-container-platform
#Add a default user admin
RUN useradd -ms /bin/bash admin

# Changed
COPY . /app/code

WORKDIR /app/code/rule_based_pipeline

RUN chown admin:admin ./pdftohtml_mod/pdftohtml_mod
RUN chgrp 0 ./pdftohtml_mod/pdftohtml_mod && \
    chmod g=u ./pdftohtml_mod/pdftohtml_mod
RUN chmod u+x ./pdftohtml_mod/pdftohtml_mod

# https://stackoverflow.com/questions/32486779/apt-add-repository-command-not-found-error-in-dockerfile
# run apt-get update && apt-get install -y software-properties-common

# https://askubuntu.com/questions/1194386/how-to-correctly-install-libpng12-0-on-the-ubuntu-19-10
# run add-apt-repository ppa:linuxuprising/libpng12
# run apt-get update
# run apt-get install libpng12-0

WORKDIR /app/code

RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1+1_ppa0_eoan_amd64.deb

RUN pip install -e .
RUN mkdir -p /app/server_logs

RUN chown admin:admin ./entry.sh
RUN chgrp 0 ./entry.sh && \
    chmod g=u ./entry.sh  
RUN chmod u+x ./entry.sh

CMD ./entry.sh
