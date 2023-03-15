FROM ubuntu:20.04

## Changed setting for open shift ---->
# https://stackoverflow.com/questions/58473832/how-do-i-change-the-permissions-in-openshift-container-platform
#Add a default user admin
RUN useradd -ms /bin/bash admin

COPY ./rule_based_pipeline /app/code/rule_based_pipeline
WORKDIR /app/code/rule_based_pipeline

RUN chown admin:admin ./pdftohtml_mod/pdftohtml_mod
RUN chgrp 0 ./pdftohtml_mod/pdftohtml_mod && \
    chmod g=u ./pdftohtml_mod/pdftohtml_mod
    
RUN chmod u+x ./pdftohtml_mod/pdftohtml_mod
## <------ Changed setting for open shift

run apt-get update && apt-get install -y software-properties-common
run add-apt-repository ppa:linuxuprising/libpng12
run apt-get update
run apt-get install libpng12-0

#RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1+1_ppa0_eoan_amd64.deb

RUN sleep infinity
