import argparse
import os
import json
import time
from datetime import timedelta
import collections
import pathlib
import shutil
import traceback

from flask import Flask, Response, request
from model_pipeline.config_farm_train import InferConfig
from model_pipeline.config_qa_farm_train import QAInferConfig
from model_pipeline.relevance_infer import TextRelevanceInfer
from model_pipeline.text_kpi_infer import TextKPIInfer

from model_pipeline.config_farm_train import ModelConfig, TrainingConfig, FileConfig, MLFlowConfig, TokenizerConfig, \
    ProcessorConfig
from model_pipeline.config_qa_farm_train import QAModelConfig, QATrainingConfig, QAFileConfig, QAMLFlowConfig, \
    QATokenizerConfig, QAProcessorConfig
from model_pipeline.farm_trainer import FARMTrainer
from model_pipeline.qa_farm_trainer import QAFARMTrainer
from kpi_inference_data_pipeline import TextKPIInferenceCurator
from kpi_inference_data_pipeline import config

import torch, gc

CLASS_DATA_TYPE_RELEVANCE = {"Text": TextRelevanceInfer}
CLASS_DATA_TYPE_KPI = {"Text": TextKPIInfer}

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATA_FOLDER = ROOT / "data"
MODEL_FOLDER = ROOT / "models"

app = Flask(__name__)


def free_memory():
    gc.collect()
    torch.cuda.empty_cache()


@app.route("/liveness")
def liveness():
    return Response(response={}, status=200)


@app.route('/train_relevance/')
def run_train_relevance():
    args = json.loads(request.args['payload'])
    project_name = args["project_name"]
    relevance_training_settings = args["train_relevance"]

    relevance_training_ouput_model_name = relevance_training_settings['output_model_name']
    free_memory()
    try:
        t1 = time.time()

        file_config = FileConfig(project_name, relevance_training_ouput_model_name)
        train_config = TrainingConfig(project_name, relevance_training_settings["seed"])
        model_config = ModelConfig(project_name)
        mlflow_config = MLFlowConfig(project_name)
        processor_config = ProcessorConfig(project_name)
        tokenizer_config = TokenizerConfig(project_name)

        #Change the default settings
        processor_config.max_seq_len = relevance_training_settings["processor"]["proc_max_seq_len"]
        processor_config.dev_split = relevance_training_settings["processor"]["proc_dev_split"]
        processor_config.label_list = relevance_training_settings["processor"]["proc_label_list"]
        processor_config.label_column_name = relevance_training_settings["processor"]["proc_label_column_name"]
        processor_config.delimiter = relevance_training_settings["processor"]["proc_delimiter"]
        processor_config.metric = relevance_training_settings["processor"]["proc_metric"]
        
        model_config.layer_dims = relevance_training_settings["model"]["model_layer_dims"]
        model_config.layer_dims = relevance_training_settings["model"]["model_lm_output_types"]

        if relevance_training_settings["input_model_name"] is not None:
            model_dir = os.path.join(str(MODEL_FOLDER), project_name, 
                                     "RELEVANCE", "Text", relevance_training_settings["input_model_name"])
            model_config.load_dir = model_dir
            tokenizer_config.pretrained_model_name_or_path = model_dir
            model_config.lang_model = model_dir
            processor_config.load_dir = model_dir
        else:
            model_dir = relevance_training_settings["base_model"]
            model_config.load_dir = None
            tokenizer_config.pretrained_model_name_or_path = relevance_training_settings["base_model"]
            processor_config.load_dir = None        
        
        train_config.n_epochs = relevance_training_settings["training"]["n_epochs"]
        train_config.run_hyp_tuning = relevance_training_settings["training"]["run_hyp_tuning"]
        train_config.use_amp = relevance_training_settings["training"]["use_amp"]
        train_config.distributed = relevance_training_settings["training"]["distributed"]
        train_config.learning_rate = relevance_training_settings["training"]["learning_rate"]
        train_config.evaluate_every = relevance_training_settings["training"]["evaluate_every"]
        train_config.dropout = relevance_training_settings["training"]["dropout"]
        train_config.batch_size = relevance_training_settings["training"]["batch_size"]
        train_config.grad_acc_steps = relevance_training_settings["training"]["grad_acc_steps"]
        train_config.run_cv = relevance_training_settings["training"]["run_cv"]  # running cross-validation won't save a model
        train_config.xval_folds = relevance_training_settings["training"]["xval_folds"]
        train_config.max_processes = relevance_training_settings["training"]["max_processes"]

        farm_trainer_class = FARMTrainer
        farm_trainer = farm_trainer_class(
            file_config=file_config,
            tokenizer_config=tokenizer_config,
            model_config=model_config,
            processor_config=processor_config,
            training_config=train_config,
            mlflow_config=mlflow_config
        )
        result = farm_trainer.run()
        
        # save results to json file
        result.pop('preds', None)
        result.pop('labels', None)
        for key in result:
            result[key] = str(result[key])
        name_out = os.path.join(str(MODEL_FOLDER), project_name, "result_rel_" + relevance_training_settings['output_model_name'] + ".json")
        with open(name_out, 'w') as f:
            json.dump(result, f)

        t2 = time.time()
    except Exception as e:
        msg = "Error during kpi infer stage\nException:" + str(repr(e) + traceback.format_exc())
        return Response(msg, status=500)

    time_elapsed = str(timedelta(seconds=t2-t1))
    msg = "Training for the relevance stage finished successfully!\nTime elapsed:{}".format(time_elapsed)
    return Response(msg, status=200)


@app.route('/infer_relevance/')
def run_infer_relevance():
    args = json.loads(request.args['payload'])
    project_name = args["project_name"]
    infer_relevance_settings = args["infer_relevance"]
    
    relevance_infer_config = InferConfig(project_name, args["train_relevance"]['output_model_name'])
    relevance_infer_config.skip_processed_files = infer_relevance_settings['skip_processed_files']
    relevance_infer_config.batch_size = infer_relevance_settings['batch_size']
    relevance_infer_config.gpu = infer_relevance_settings['gpu']
    relevance_infer_config.num_processes = infer_relevance_settings['num_processes']
    relevance_infer_config.disable_tqdm = infer_relevance_settings['disable_tqdm']
    relevance_infer_config.kpi_questions = infer_relevance_settings['kpi_questions']
    relevance_infer_config.sectors = infer_relevance_settings['sectors']
    relevance_infer_config.return_class_probs = infer_relevance_settings['return_class_probs']

    shutil.copyfile(os.path.join(DATA_FOLDER, project_name, "input", "kpi_mapping", "kpi_mapping.csv"), "/kpi_mapping.csv")
    free_memory()

    try:
        t1 = time.time()
        for data_type in relevance_infer_config.data_types:
            rel_infer_component_class = CLASS_DATA_TYPE_RELEVANCE[data_type]
            rel_infer_component_obj = rel_infer_component_class(relevance_infer_config)
            result_rel = rel_infer_component_obj.run_folder()
        t2 = time.time()
    except Exception as e:
        msg = "Error during kpi infer stage\nException:" + str(repr(e) + traceback.format_exc())
        return Response(msg, status=500)

    time_elapsed = str(timedelta(seconds=t2-t1))
    msg = "Inference for the relevance stage finished successfully!\nTime elapsed:{}".format(time_elapsed)
    return Response(msg, status=200)


@app.route('/train_kpi/')
def run_train_kpi():
    args = json.loads(request.args['payload'])
    project_name = args["project_name"]
    kpi_inference_training_settings = args["train_kpi"]

    file_config = QAFileConfig(project_name, kpi_inference_training_settings['output_model_name'])

    config.TextKPIInferenceCurator_kwargs = {
        "annotation_folder": DATA_FOLDER / project_name / "interim" / "ml" / "annotations",
        "agg_annotation": DATA_FOLDER / project_name / "interim" / "ml" / "annotations" / "aggregated_annotation.csv",
        "extracted_text_json_folder": DATA_FOLDER / project_name / "interim" / "ml" / "extraction",
        "output_squad_folder": DATA_FOLDER / project_name /  "interim" / "ml" / "training",
        "relevant_text_path": DATA_FOLDER / project_name / "interim" / "ml" / "text_3434.csv"
    }
    config.seed = kpi_inference_training_settings['seed']

    free_memory()
    try:
        t1 = time.time()
        
        tkpi = TextKPIInferenceCurator(**config.TextKPIInferenceCurator_kwargs)
        tkpi.annotation_folder = file_config.annotation_dir
        tkpi.agg_annotation = os.path.join(file_config.annotation_dir, "aggregated_annotation.csv")
        tkpi.output_squad_folder = file_config.training_dir
        tkpi.relevant_text_path = os.path.join(file_config.data_dir, project_name, "interim", "ml", "text_3434.csv")
        curation_input = kpi_inference_training_settings["curation"]
        _, _ = tkpi.curate(curation_input["val_ratio"], curation_input["seed"], curation_input["find_new_answerable"], curation_input["create_unanswerable"])

        print('Curation step in train_kpi done.')
        
        free_memory()

        train_config = QATrainingConfig(project_name, kpi_inference_training_settings['seed'])
        model_config = QAModelConfig(project_name)
        mlflow_config = QAMLFlowConfig(project_name)
        processor_config = QAProcessorConfig(project_name)
        tokenizer_config = QATokenizerConfig(project_name)

        file_config.perform_splitting = kpi_inference_training_settings["data"]["perform_splitting"]
        file_config.dev_split = kpi_inference_training_settings["data"]["dev_split"]
        train_config.run_hyp_tuning = kpi_inference_training_settings["training"]["run_hyp_tuning"]
        train_config.use_amp = kpi_inference_training_settings["training"]["use_amp"]
        train_config.distributed = kpi_inference_training_settings["training"]["distributed"]
        train_config.learning_rate = kpi_inference_training_settings["training"]["learning_rate"]
        train_config.n_epochs = kpi_inference_training_settings["training"]["n_epochs"]
        train_config.evaluate_every = kpi_inference_training_settings["training"]["evaluate_every"]
        train_config.dropout = kpi_inference_training_settings["training"]["dropout"]
        train_config.batch_size = kpi_inference_training_settings["training"]["batch_size"]
        train_config.grad_acc_steps = kpi_inference_training_settings["training"]["grad_acc_steps"]
        train_config.run_cv = kpi_inference_training_settings["training"]["run_cv"]
        train_config.xval_folds = kpi_inference_training_settings["training"]["xval_folds"]
        train_config.max_processes = kpi_inference_training_settings["training"]["max_processes"]
        model_config.layer_dims = kpi_inference_training_settings["model"]["model_layer_dims"]
        model_config.lm_output_types = kpi_inference_training_settings["model"]["model_lm_output_types"]
        mlflow_config.track_experiment = kpi_inference_training_settings["mlflow"]["track_experiment"]
        mlflow_config.url = kpi_inference_training_settings["mlflow"]["url"]
        processor_config.max_seq_len = kpi_inference_training_settings["processor"]["max_seq_len"]
        processor_config.label_list = kpi_inference_training_settings["processor"]["label_list"]
        processor_config.metric = kpi_inference_training_settings["processor"]["metric"]
        
        if kpi_inference_training_settings["input_model_name"] is not None:
            model_dir = os.path.join(str(MODEL_FOLDER), project_name, 
                                     "KPI_EXTRACTION", "Text", kpi_inference_training_settings["input_model_name"])
            model_config.load_dir = model_dir
            tokenizer_config.pretrained_model_name_or_path = model_dir
            model_config.lang_model = model_dir
        else:
            tokenizer_config.pretrained_model_name_or_path = kpi_inference_training_settings["base_model"]
            model_config.load_dir = None
            model_config.lang_model = kpi_inference_training_settings["base_model"]

        farm_trainer_class = QAFARMTrainer
        farm_trainer = farm_trainer_class(
            file_config =file_config,
            tokenizer_config=tokenizer_config,
            model_config=model_config,
            processor_config=processor_config,
            training_config=train_config,
            mlflow_config=mlflow_config
        )
        
        result = farm_trainer.run()
        
        # save results to json file
        result.pop('preds', None)
        result.pop('labels', None)
        for key in result:
            result[key] = str(result[key])
        name_out = os.path.join(str(MODEL_FOLDER), project_name, "result_kpi_" + kpi_inference_training_settings['output_model_name'] + ".json")
        with open(name_out, 'w') as f:
            json.dump(result, f)
            
        t2 = time.time()

    except Exception as e:
        msg = "Error during kpi infer stage\nException:" + str(repr(e) + traceback.format_exc())
        return Response(msg, status=500)
    time_elapsed = str(timedelta(seconds=t2-t1))
    msg = "Training for the kpi extraction stage finished successfully!\nTime elapsed:{}".format(time_elapsed)
    return Response(msg, status=200)


@app.route('/infer_kpi/')
def run_infer_kpi():
    args = json.loads(request.args['payload'])
    project_name = args["project_name"]
    
    relevance_infer_config = InferConfig(project_name, args["train_relevance"]['output_model_name'])
    qa_infer_config = QAInferConfig(project_name, args["train_kpi"]['output_model_name'])
    
    qa_infer_config.skip_processed_files = args["infer_kpi"]['skip_processed_files']
    qa_infer_config.top_k = args["infer_kpi"]['top_k']
    qa_infer_config.batch_size = args["infer_kpi"]['batch_size']
    qa_infer_config.num_processes = args["infer_kpi"]['num_processes']
    qa_infer_config.no_ans_boost = args["infer_kpi"]['no_ans_boost']
    
    free_memory()
    try:
        t1 = time.time()
        for data_type in qa_infer_config.data_types:
            relevance_result_dir = relevance_infer_config.result_dir[data_type]
            kpi_infer_component_class = CLASS_DATA_TYPE_KPI[data_type]
            kpi_infer_component_obj = kpi_infer_component_class(qa_infer_config)
            result_kpi = kpi_infer_component_obj.infer_on_relevance_results(relevance_result_dir)
        t2 = time.time()
    except Exception as e:
        msg = "Error during kpi infer stage\nException:" + str(repr(e) + traceback.format_exc())
        return Response(msg, status=500)
    time_elapsed = str(timedelta(seconds=t2-t1))
    msg = "Inference for the kpi extraction stage finished successfully!\nTime elapsed:{}".format(time_elapsed)
    return Response(msg, status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='inference server')
    # Add the arguments
    parser.add_argument('--port',
                        type=int,
                        default=6000,
                        help='port to use for the infer server')
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)
