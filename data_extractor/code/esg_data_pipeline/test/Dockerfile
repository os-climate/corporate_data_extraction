FROM ubuntu:20.04

# no prompt during installation:
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils wget python3 python3-pip vim

COPY . /app/code

WORKDIR /app/code

RUN pip install -r requirements.txt

CMD python3 app.py
