import argparse
import os
import json
import time
from datetime import timedelta
import collections
import pathlib
import shutil
import traceback
from s3_communication import S3Communication
import zipfile

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


def create_directory(directory_name):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


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
        
        s3_usage = args["s3_usage"]
        if s3_usage:
            s3_settings = args["s3_settings"]
            project_prefix_data = s3_settings['prefix'] + "/" + project_name + '/data'
            project_prefix_project_models = s3_settings['prefix'] + "/" + project_name + '/models'
            # init s3 connector
            s3c_main = S3Communication(
                s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
                aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
                aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
                s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
            )
            s3c_interim = S3Communication(
                s3_endpoint_url=os.getenv(s3_settings['interim_bucket']['s3_endpoint']),
                aws_access_key_id=os.getenv(s3_settings['interim_bucket']['s3_access_key']),
                aws_secret_access_key=os.getenv(s3_settings['interim_bucket']['s3_secret_key']),
                s3_bucket=os.getenv(s3_settings['interim_bucket']['s3_bucket_name']),
            )
            create_directory(os.path.dirname(file_config.curated_data))
            s3c_interim.download_files_in_prefix_to_dir(project_prefix_data + '/interim/ml/curation', 
                                    os.path.dirname(file_config.curated_data))
        
        training_folder = DATA_FOLDER / project_name / 'interim/ml/training'
        create_directory(training_folder)
        output_model_folder = os.path.join(str(MODEL_FOLDER), file_config.experiment_name, file_config.experiment_type, 
                         file_config.data_type, file_config.output_model_name)
        create_directory(output_model_folder)
        
        if relevance_training_settings["input_model_name"] is not None:
            base_model_dir = os.path.join(str(MODEL_FOLDER), project_name, "RELEVANCE", "Text")
            model_dir = os.path.join(base_model_dir, relevance_training_settings["input_model_name"])
            model_config.load_dir = model_dir
            tokenizer_config.pretrained_model_name_or_path = model_dir
            model_config.lang_model = model_dir
            processor_config.load_dir = model_dir
            if args['s3_usage']:
                # Download model
                model_rel_prefix = str(pathlib.Path(s3_settings['prefix']) / project_name / 'models' / 'RELEVANCE' / 'Text')
                output_model_zip = model_dir + ".zip"
                s3c_main.download_file_from_s3(output_model_zip, model_inf_prefix, relevance_training_settings["input_model_name"] + ".zip")
                with zipfile.ZipFile(output_model_zip, 'r') as zip_ref:
                    zip_ref.extractall(base_model_dir)
                os.remove(output_model_zip)
        else:
            model_config.lang_model = relevance_training_settings["base_model"]
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
        
        if s3_usage:
            train_rel_prefix = os.path.join(project_prefix_project_models, file_config.experiment_type, file_config.data_type)
            output_model_zip = os.path.join(str(MODEL_FOLDER), file_config.experiment_name, file_config.experiment_type, 
                 file_config.data_type, file_config.output_model_name + ".zip")
            with zipfile.ZipFile(output_model_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipdir(output_model_folder, zipf)            
            response = s3c_main.upload_file_to_s3(filepath=output_model_zip,
                                             s3_prefix=train_rel_prefix,
                                             s3_key=file_config.output_model_name + ".zip")
            response_2 = s3c_main.upload_file_to_s3(filepath=name_out,
                                 s3_prefix=train_rel_prefix,
                                 s3_key="result_rel_" + file_config.output_model_name + ".json")
            create_directory(output_model_folder)
            create_directory(training_folder)
            create_directory(os.path.dirname(file_config.curated_data))
            if relevance_training_settings["input_model_name"] is not None:
                create_directory(model_dir)
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
    
    BASE_DATA_PROJECT_FOLDER =  DATA_FOLDER / project_name
    BASE_INTERIM_FOLDER = BASE_DATA_PROJECT_FOLDER / 'interim' / 'ml'
    BASE_OUTPUT_FOLDER = BASE_DATA_PROJECT_FOLDER / 'output' / relevance_infer_config.experiment_type / relevance_infer_config.data_type
    ANNOTATION_FOLDER = BASE_INTERIM_FOLDER / 'annotations'
    EXTRACTION_FOLDER = BASE_INTERIM_FOLDER / 'extraction'

    kpi_folder = os.path.join(DATA_FOLDER, project_name, "input", "kpi_mapping")

    output_model_folder = os.path.join(str(MODEL_FOLDER), project_name, relevance_infer_config.experiment_type, 
                                       relevance_infer_config.data_type)

    create_directory(kpi_folder)
    create_directory(output_model_folder)
    create_directory(BASE_OUTPUT_FOLDER)
    create_directory(ANNOTATION_FOLDER)
    create_directory(EXTRACTION_FOLDER)
    
    s3_usage = args["s3_usage"]
    if s3_usage:
        s3_settings = args["s3_settings"]
        project_prefix_data = s3_settings['prefix'] + "/" + project_name + '/data'
        project_prefix_project_models = s3_settings['prefix'] + "/" + project_name + '/models'
        # init s3 connector
        s3c_main = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
            aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
            aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
            s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
        )
        s3c_interim = S3Communication(
                s3_endpoint_url=os.getenv(s3_settings['interim_bucket']['s3_endpoint']),
                aws_access_key_id=os.getenv(s3_settings['interim_bucket']['s3_access_key']),
                aws_secret_access_key=os.getenv(s3_settings['interim_bucket']['s3_secret_key']),
                s3_bucket=os.getenv(s3_settings['interim_bucket']['s3_bucket_name']),
        )
        # Download kpi file
        s3c_main.download_files_in_prefix_to_dir(project_prefix_data + '/input/kpi_mapping', kpi_folder)
        # Download model
        train_rel_prefix = os.path.join(project_prefix_project_models, relevance_infer_config.experiment_type, relevance_infer_config.data_type)
        output_model_zip = os.path.join(output_model_folder, args["train_relevance"]['output_model_name'] + ".zip")
        s3c_main.download_file_from_s3(output_model_zip, train_rel_prefix, args["train_relevance"]['output_model_name'] + ".zip")
        with zipfile.ZipFile(output_model_zip, 'r') as zip_ref:
            zip_ref.extractall(output_model_folder)
        os.remove(output_model_zip)
        # Download extraction files
        s3c_interim.download_files_in_prefix_to_dir(project_prefix_data + '/interim/ml/extraction', 
                            EXTRACTION_FOLDER)
        # Download annotation files        
        s3c_interim.download_files_in_prefix_to_dir(project_prefix_data + '/interim/ml/annotations', 
                                    ANNOTATION_FOLDER)
        
    shutil.copyfile(os.path.join(kpi_folder, "kpi_mapping.csv"), "/app/code/kpi_mapping.csv")
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
    
    if s3_usage:
        project_prefix_project_output = pathlib.Path(s3_settings['prefix'] + "/" + project_name + '/output') \
                / relevance_infer_config.experiment_type / relevance_infer_config.data_type
        s3c_main.upload_files_in_dir_to_prefix(BASE_OUTPUT_FOLDER,  project_prefix_project_output)
        create_directory(kpi_folder)
        create_directory(str(pathlib.Path(output_model_folder) / args["train_relevance"]['output_model_name']))
        create_directory(BASE_OUTPUT_FOLDER)
        create_directory(ANNOTATION_FOLDER)
        create_directory(EXTRACTION_FOLDER)
    
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
        
        create_directory(tkpi.annotation_folder)
        create_directory(str(pathlib.Path(file_config.data_dir) / project_name / "interim" / "ml"))
        create_directory(tkpi.output_squad_folder)
        
        if args['s3_usage']:
            s3_settings = args["s3_settings"]
            s3c_main = S3Communication(
                    s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
                    aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
                    aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
                    s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
                )
            s3c_interim = S3Communication(
                    s3_endpoint_url=os.getenv(s3_settings['interim_bucket']['s3_endpoint']),
                    aws_access_key_id=os.getenv(s3_settings['interim_bucket']['s3_access_key']),
                    aws_secret_access_key=os.getenv(s3_settings['interim_bucket']['s3_secret_key']),
                    s3_bucket=os.getenv(s3_settings['interim_bucket']['s3_bucket_name']),
                )
            project_prefix_data = pathlib.Path(s3_settings['prefix']) / project_name / 'data'
            project_prefix_agg_annotations = str(project_prefix_data / 'interim' / 'ml' / 'annotations')
            
            # Download aggregated annotations file
            s3c_interim.download_file_from_s3(filepath=tkpi.agg_annotation,
                          s3_prefix=project_prefix_agg_annotations,
                          s3_key='aggregated_annotation.csv')
            
            # Download kpi file
            s3c_main.download_file_from_s3('/app/code/kpi_mapping.csv', s3_prefix=str(project_prefix_data / 'input' / 'kpi_mapping'), s3_key='kpi_mapping.csv')
            
            # Download text_3434 file
            s3c_interim.download_file_from_s3(tkpi.relevant_text_path, s3_prefix=str(project_prefix_data / 'interim' / 'ml'), s3_key='text_3434.csv')
            
            # Download extractions
            s3c_interim.download_files_in_prefix_to_dir(str(project_prefix_data / 'interim' / 'ml' / 'extraction'), 
                        str(config.TextKPIInferenceCurator_kwargs['extracted_text_json_folder']))
        
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
            base_model_dir = os.path.join(str(MODEL_FOLDER), project_name, "KPI_EXTRACTION", "Text")
            model_dir = os.path.join(base_model_dir, kpi_inference_training_settings["input_model_name"])
            model_config.load_dir = model_dir
            tokenizer_config.pretrained_model_name_or_path = model_dir
            model_config.lang_model = model_dir
            if args['s3_usage']:
                # Download model
                model_inf_prefix = str(pathlib.Path(s3_settings['prefix']) / project_name / 'models' / 'KPI_EXTRACTION' / 'Text')
                output_model_zip = model_dir + ".zip"
                s3c_main.download_file_from_s3(output_model_zip, model_inf_prefix, kpi_inference_training_settings["input_model_name"] + ".zip")
                with zipfile.ZipFile(output_model_zip, 'r') as zip_ref:
                    zip_ref.extractall(base_model_dir)
                os.remove(output_model_zip)
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
        
        if args['s3_usage']:
            print('Next we store the files to S3.')
            train_inf_prefix = str(pathlib.Path(s3_settings['prefix']) / project_name / 'models' / 'KPI_EXTRACTION' / 'Text')
            output_model_folder = str(pathlib.Path(MODEL_FOLDER) / project_name / "KPI_EXTRACTION" / "Text" / kpi_inference_training_settings['output_model_name'])
            print('First we zip the model. This can take some time.')
            with zipfile.ZipFile(output_model_folder + ".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipdir(output_model_folder, zipf)            
            print('Next we upload the model to S3. This can take some time.')
            response = s3c_main.upload_file_to_s3(filepath=output_model_folder + ".zip",
                                              s3_prefix=train_inf_prefix,
                                              s3_key=kpi_inference_training_settings['output_model_name'] + ".zip")
            os.remove(output_model_folder + ".zip")
            print('Next we upload the interim training files and the statistics to S3.')
            response_2 = s3c_main.upload_file_to_s3(filepath=name_out,
                                  s3_prefix=train_inf_prefix,
                                  s3_key="result_kpi_" + kpi_inference_training_settings['output_model_name'] + ".json")
            s3c_interim.upload_files_in_dir_to_prefix(source_dir=str(DATA_FOLDER / project_name / 'interim' / 'ml' / 'training'),
                                                      s3_prefix=str(pathlib.Path(s3_settings['prefix']) / project_name / 'data' / 'interim' / 'ml' / 'training'))
            create_directory(output_model_folder)
            create_directory(output_model_folder)
            create_directory(os.path.join(str(MODEL_FOLDER), project_name))
            create_directory(tkpi.annotation_folder)
            create_directory(str(pathlib.Path(file_config.data_dir) / project_name / "interim" / "ml"))
            create_directory(str(project_prefix_data / 'input'))
            create_directory(tkpi.output_squad_folder)
            create_directory(str(config.TextKPIInferenceCurator_kwargs['extracted_text_json_folder']))
            if kpi_inference_training_settings["input_model_name"] is not None:
                create_directory(model_dir)
        
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
