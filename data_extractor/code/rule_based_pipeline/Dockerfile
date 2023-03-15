FROM ubuntu:20.04

RUN useradd -ms /bin/bash admin

COPY ./rule_based_pipeline /app/code/rule_based_pipeline
WORKDIR /app/code/rule_based_pipeline

RUN mkdir test

RUN chown -R admin:admin ./test

CMD sleep infinity
