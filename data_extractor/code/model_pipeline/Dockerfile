ARG PYTORCH="1.6.0"
ARG CUDA="10.1"
ARG CUDNN="7"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel
ENV TORCH_CUDA_ARCH_LIST="3.7 6.0 6.1 7.0+PTX"

#ENV http_proxy="http://proxy-ids-poc-d.we1.azure.aztec.cloud.allianz:80"
#ENV https_proxy="http://proxy-ids-poc-d.we1.azure.aztec.cloud.allianz:80"

RUN apt-key del 3bf863cc
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub

RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get update
RUN apt-get install -y unzip vim

COPY ./model_pipeline /app/code/model_pipeline
COPY ./kpi_inference_data_pipeline /app/code/kpi_inference_data_pipeline

WORKDIR /app/code/kpi_inference_data_pipeline
RUN pip install -e .

WORKDIR /app/code/model_pipeline
RUN pip install -e .

RUN mkdir -p /app/server_logs
RUN chmod u+x entry.sh
CMD ./entry.sh
