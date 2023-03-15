FROM ubuntu:20.04

## Changed setting for open shift ------------------------------------------------->
# https://stackoverflow.com/questions/58473832/how-do-i-change-the-permissions-in-openshift-container-platform
#Add a default user admin
RUN useradd -ms /bin/bash admin

COPY ./rule_based_pipeline /app/code/rule_based_pipeline
WORKDIR /app/code/rule_based_pipeline

RUN chown admin:admin ./pdftohtml_mod/pdftohtml_mod
RUN chgrp 0 ./pdftohtml_mod/pdftohtml_mod && \
    chmod g=u ./pdftohtml_mod/pdftohtml_mod
    
RUN chmod u+x ./pdftohtml_mod/pdftohtml_mod

# https://stackoverflow.com/questions/32486779/apt-add-repository-command-not-found-error-in-dockerfile
run apt-get update && apt-get install -y software-properties-common

# https://askubuntu.com/questions/1194386/how-to-correctly-install-libpng12-0-on-the-ubuntu-19-10
run add-apt-repository ppa:linuxuprising/libpng12
run apt-get update
run apt-get install libpng12-0
## <-------------------------------------------------- Changed setting for open shift

RUN pip install -e .

RUN mkdir -p /app/server_logs

RUN chmod u+x entry.sh
CMD ./entry.sh
