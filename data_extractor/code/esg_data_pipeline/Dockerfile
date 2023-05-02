FROM ubuntu:20.04

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils wget python3 python3-pip vim libcurl3-gnutls

COPY entry.sh .

RUN chgrp -R 0 ./entry.sh && chmod g=u ./entry.sh
RUN chmod -R a+x ./entry.sh

USER 1234

CMD ./entry.sh
