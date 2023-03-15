FROM ubuntu:20.04

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
