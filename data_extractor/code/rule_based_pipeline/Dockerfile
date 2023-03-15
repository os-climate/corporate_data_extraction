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

# Changed
COPY . /app/code

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod u+x /app/code

WORKDIR /app/code

RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1+1_ppa0_eoan_amd64.deb
RUN pip install -e .
RUN mkdir -p /app/server_logs

USER 1234

CMD ./entry.sh
