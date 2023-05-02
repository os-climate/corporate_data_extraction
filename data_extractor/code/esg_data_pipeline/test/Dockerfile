FROM ubuntu:20.04

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils wget python3 python3-pip vim libcurl3-gnutls

COPY app.py /app/code/app.py
COPY requirements.txt /app/code/requirements.txt
COPY entry.sh /app/code/entry.sh

WORKDIR /app/code

RUN pip install -r requirements.txt

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod -R a+x /app/code

USER 1234

CMD ./entry.sh
