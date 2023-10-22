# Modified mmdetection Dockerfile
ARG PYTORCH="1.4"
ARG CUDA="10.1"
ARG CUDNN="7"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

ENV TORCH_CUDA_ARCH_LIST="3.7 6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

RUN apt-key del 3bf863cc
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub

RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

# Added poppler-utils, default-jre installations
RUN apt-get update && apt-get install -y git wget vim ninja-build poppler-utils default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./esg_data_pipeline /app/code/esg_data_pipeline
COPY ./utils/s3_communication.py /app/code/esg_data_pipeline/esg_data_pipeline/s3_communication.py

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod -R 777 /app/code

WORKDIR /app/code/esg_data_pipeline

RUN pip install -e .

RUN mkdir -p /app/server_logs
RUN chmod -R 777 /app/server_logs

RUN mkdir -p /app/data
RUN chmod -R 777 /app/data

CMD ./entry.sh


