import argparse
import requests
import shutil
import os
import glob
import json
import yaml
import pandas as pd
import traceback
import pickle
import datetime
from utils.s3_communication import S3Communication
from pathlib import Path
from utils.paths import path_file_running
from utils.utils import link_files, link_extracted_files, copy_file_without_overwrite, save_train_info
from utils.core_utils import create_folder
from utils.training_monitor import TrainingMonitor
from utils.settings import get_s3_settings, get_main_settings, S3Settings, MainSettings, Settings
from utils.converter import XlsToCsvConverter
from utils.router import Router
from utils.core_utils import download_data_from_s3_main_bucket_to_local_folder_if_required,\
upload_data_from_local_folder_to_s3_interim_bucket_if_required
from utils.paths import ProjectPaths


project_settings = None
source_pdf = None
source_annotation = None
source_mapping = None
folder_text_3434 = None
folder_relevance = None
project_prefix = None
s3_usage = None
s3c_main = None
s3c_interim = None
project_prefix = None





def main():
    s3_settings: S3Settings = get_s3_settings()
    main_settings: MainSettings = get_main_settings()

    training_monitor = TrainingMonitor(path_file_running)
    converter = XlsToCsvConverter()
    # router = Router()
    
    global project_settings
    global source_pdf
    global source_annotation
    global source_mapping
    global folder_text_3434
    global folder_relevance
    global project_prefix

    if training_monitor.check_running():
        print("Another training or inference process is currently running.")
        return

    # -- SysInReaderClass start
    parser = argparse.ArgumentParser(description='End-to-end inference')
    
    # Add the arguments
    parser.add_argument('--project_name',
                        type=str,
                        default=None,
                        help='Name of the Project')

    parser.add_argument('--s3_usage',
                        type=str,
                        default=None,
                        help='Do you want to use S3? Type either Y or N.')
     
    args = parser.parse_args()
    project_name = args.project_name
    if project_name is None:
        project_name = input("What is the project name? ")
    if project_name is None or project_name=="":
        print("project name must not be empty")
        return

    s3_usage = args.s3_usage
    if s3_usage is None:
        s3_usage = input('Do you want to use S3? Type either Y or N.')
    if s3_usage is None or str(s3_usage) not in ['Y', 'N']:
        print("Answer to S3 usage must by Y or N. Stop program. Please restart.")
        return None
    else:
        s3_usage = s3_usage == 'Y'
    # -- SysInReaderClass end
    project_paths: ProjectPaths = ProjectPaths(project_name, main_settings)
    project_data_dir: str = str(project_paths.path_project_data_folder)
    router = Router(main_settings, s3_settings, project_paths)

    create_folder(Path(project_data_dir))
    s3c_main = None
    s3c_interim = None
    if s3_usage:
        # Opening s3 settings file
        s3_settings_path = str(project_paths.PATH_FOLDER_DATA) + r'/' + 's3_settings.yaml'
        f = open(s3_settings_path, 'r')
        s3_settings = yaml.safe_load(f)
        s3_settings = S3Settings(**s3_settings)
        f.close()
        project_prefix = s3_settings.prefix + "/" + project_name + '/data'
        # init s3 connector
        s3c_main = S3Communication(
                                    s3_endpoint_url=os.getenv(s3_settings.main_bucket.s3_endpoint),
                                    aws_access_key_id=os.getenv(s3_settings.main_bucket.s3_access_key),
                                    aws_secret_access_key=os.getenv(s3_settings.main_bucket.s3_secret_key),
                                    s3_bucket=os.getenv(s3_settings.main_bucket.s3_bucket_name),
        )
        s3c_interim = S3Communication(
                                    s3_endpoint_url=os.getenv(s3_settings.interim_bucket.s3_endpoint),
                                    aws_access_key_id=os.getenv(s3_settings.interim_bucket.s3_access_key),
                                    aws_secret_access_key=os.getenv(s3_settings.interim_bucket.s3_secret_key),
                                    s3_bucket=os.getenv(s3_settings.interim_bucket.s3_bucket_name),
        )
        settings_path = project_data_dir + "/settings.yaml"
        s3c_main.download_file_from_s3(filepath=settings_path,
                                       s3_prefix=project_prefix,
                                       s3_key='settings.yaml')

    # Opening YAML file
    # f = open(project_data_dir + r'/settings.yaml', 'r')
    # project_settings = yaml.safe_load(f)
    # f.close()

    with open(project_data_dir + r'/settings.yaml', 'r') as file:
        project_settings_loaded = yaml.safe_load(file)
        project_settings = MainSettings(**project_settings_loaded)

    # project_settings.update({'s3_usage': s3_usage})
    project_settings.general.s3_usage = s3_usage
    if s3_usage:
        # project_settings.update({'s3_settings': s3_settings})
        project_settings.s3_settings = s3_settings
    
    training_monitor.set_running()
    try:
        converter.path_folder_source = project_paths.path_folder_source_annotation
        converter.path_folder_destination = project_paths.path_folder_destination_annotation

        create_folder(project_paths.path_folder_source_pdf)
        create_folder(project_paths.path_folder_source_annotation)
        create_folder(project_paths.path_folder_source_mapping)
        create_folder(project_paths.path_folder_text_3434)
        create_folder(project_paths.path_folder_destination_pdf)
        create_folder(project_paths.path_folder_destination_annotation)
        create_folder(project_paths.path_folder_destination_mapping)
        create_folder(project_paths.path_folder_destination_extraction)
        create_folder(project_paths.path_folder_destination_training)
        create_folder(project_paths.path_folder_destination_curation)
        # if project_settings['train_relevance']['train']:
        if project_settings.train_relevance.train:
            create_folder(project_paths.path_folder_destination_saved_models_relevance)
        if project_settings.train_kpi.train:
            create_folder(project_paths.path_folder_destination_saved_models_inference)
        create_folder(project_paths.path_folder_relevance)

        link_files(project_paths.path_folder_source_pdf, project_paths.path_folder_destination_pdf)
        link_files(project_paths.path_folder_source_annotation, project_paths.path_folder_destination_annotation)
        link_files(project_paths.path_folder_source_mapping, project_paths.path_folder_destination_mapping)
        if project_settings.extraction.use_extractions:
            path_source_extraction: Path = Path(project_data_dir) / Path('output/TEXT_EXTRACTION')
            if path_source_extraction.exists():
                link_extracted_files(path_source_extraction, project_paths.path_folder_source_pdf, project_paths.path_folder_destination_extraction)
        
        download_data_from_s3_main_bucket_to_local_folder_if_required(s3c_main, source_annotation, 
                                                                      Path(s3_settings.prefix) / Path('input/annotations'), 
                                                                      project_settings)
        converter.convert()
        upload_data_from_local_folder_to_s3_interim_bucket_if_required(s3c_interim, 
                                                                       project_paths.path_folder_destination_annotation, 
                                                                       Path(s3_settings.prefix) / Path('interim/ml/annotations'),
                                                                       project_settings)

        router.run_router()
        end_to_end_response = router.return_value
        
        if end_to_end_response:
            if project_settings.extraction.store_extractions:
                print("Finally we transfer the text extraction to the output folder")
                source_extraction_data: Path = project_paths.path_folder_destination_extraction
                destination_extraction_data = project_data_dir + r'/output/TEXT_EXTRACTION'
                if s3_usage:
                    s3c_interim.download_files_in_prefix_to_dir(project_prefix + '/interim/ml/extraction', 
                                                                source_extraction_data, project_settings)
                    s3c_main.upload_files_in_dir_to_prefix(source_extraction_data, 
                                                           project_prefix + '/output/TEXT_EXTRACTION', project_settings)
                else:
                    os.makedirs(destination_extraction_data, exist_ok=True)
                    end_to_end_response = copy_file_without_overwrite(str(source_extraction_data),
                                                                      destination_extraction_data)
                
            if project_settings.general.delete_interim_files:
                create_folder(project_paths.path_folder_destination_pdf)
                create_folder(project_paths.path_folder_destination_mapping)
                create_folder(project_paths.path_folder_destination_annotation)
                create_folder(project_paths.path_folder_destination_extraction)
                create_folder(project_paths.path_folder_destination_training)
                create_folder(project_paths.path_folder_destination_curation)
                create_folder(project_paths.path_folder_text_3434)
                if s3_usage:
                    # Show only objects which satisfy our prefix
                    my_bucket = s3c_interim.s3_resource.Bucket(name=s3c_interim.bucket)
                    for objects in my_bucket.objects.filter(Prefix=project_prefix+'/interim'):
                        _ = objects.delete()
                
            if end_to_end_response:
                save_train_info(project_name, s3_usage, s3c_main)
                print("End-to-end inference complete")

    except Exception as e:
        print('Process failed to run. Reason: ' + str(repr(e)) + traceback.format_exc())

    training_monitor.clear_running()


if __name__ == "__main__":
    main()
