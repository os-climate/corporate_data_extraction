FROM ubuntu:20.04

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils wget python3 python3-pip vim libcurl3-gnutls

COPY app.py .
COPY requirements.txt .
COPY entry.sh .
RUN pip install -r requirements.txt

CMD ./entry.sh