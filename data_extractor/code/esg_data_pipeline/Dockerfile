# Modified mmdetection Dockerfile
ARG PYTORCH="1.4"
ARG CUDA="10.1"
ARG CUDNN="7"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

ENV TORCH_CUDA_ARCH_LIST="3.7 6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

#ENV http_proxy="http://proxy-ids-poc-d.we1.azure.aztec.cloud.allianz:80"
#ENV https_proxy="http://proxy-ids-poc-d.we1.azure.aztec.cloud.allianz:80"

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
RUN pip install --no-cache-dir -e .

# Reinstall openmm-mmcv to use the right version, somehow the above installation
# of mmdetection installs mmcv of an updated version which is not compatible for
# mmdetection v1.2
RUN pip install mmcv==0.5.7

# Install our package
COPY . /app/code

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod -R a+x /app/code

WORKDIR /app/code

RUN pip install -e .
RUN mkdir -p /app/server_logs

USER 1234

CMD ./entry.sh


