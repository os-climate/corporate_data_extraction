ARG PYTORCH="1.6.0"
ARG CUDA="10.1"
ARG CUDNN="7"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel
ENV TORCH_CUDA_ARCH_LIST="3.7 6.0 6.1 7.0+PTX"

RUN apt-key del 3bf863cc
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub

RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get update
RUN apt-get install -y unzip vim wget

COPY ./model_pipeline /app/code/model_pipeline
COPY ./kpi_inference_data_pipeline /app/code/kpi_inference_data_pipeline

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod -R a+x /app/code

WORKDIR /app/code/kpi_inference_data_pipeline
RUN pip install -e .

WORKDIR /app/code/model_pipeline
RUN pip install -e .

RUN mkdir -p /app/server_logs
RUN chmod -R 777 /app/server_logs

#USER 1234

CMD ./entry.sh
