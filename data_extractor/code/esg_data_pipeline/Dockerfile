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
RUN apt-get update && apt-get install -y git vim ninja-build poppler-utils default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install mmdetection
RUN conda clean --all
RUN git clone --branch v1.2.0 https://github.com/open-mmlab/mmdetection.git /mmdetection
WORKDIR /mmdetection
ENV FORCE_CUDA="1"
RUN pip install cython --no-cache-dir
RUN pip install "git+https://github.com/open-mmlab/cocoapi.git#subdirectory=pycocotools"

COPY ./esg_data_pipeline /app/code/esg_data_pipeline

RUN chgrp -R 0 /app/code/esg_data_pipeline && chmod g=u /app/code/esg_data_pipeline
RUN chmod -R a+x /app/code/esg_data_pipeline

WORKDIR /app/code/esg_data_pipeline

#RUN pip install -e .
RUN mkdir -p /app/server_logs

USER 1234

CMD ./entry.sh
