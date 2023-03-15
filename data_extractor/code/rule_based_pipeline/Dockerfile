FROM ubuntu:20.04

RUN useradd -ms /bin/bash admin

COPY ./rule_based_pipeline /app/code/rule_based_pipeline
WORKDIR /app/code/rule_based_pipeline

RUN chown -R admin:admin .

RUN chgrp -R 0 . && chmod -R g=u .

RUN chmod -R 775 .

CMD sleep infinity
