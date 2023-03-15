FROM ubuntu:20.04

RUN useradd -ms /bin/bash admin

COPY ./rule_based_pipeline /app/code/rule_based_pipeline
WORKDIR /app/code/rule_based_pipeline

RUN chown admin:admin ./pdftohtml_mod/pdftohtml_mod
RUN chgrp 0 ./pdftohtml_mod/pdftohtml_mod && \
    chmod g=u ./pdftohtml_mod/pdftohtml_mod
    
RUN chmod u+x ./pdftohtml_mod/pdftohtml_mod

#WORKDIR /app/code/rule_based_pipeline
#RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1+1_ppa0_eoan_amd64.deb
#RUN pip install -e .

#RUN mkdir -p /app/server_logs

#RUN chmod u+x entry.sh
#CMD ./entry.sh
CMD sleep infinity
