FROM ubuntu:20.04

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils wget python3 python3-pip vim

COPY . /app/code

WORKDIR /app/code

RUN pip install -r requirements.txt

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod -R a+x /app/code

USER 1234

CMD python3 app.py
