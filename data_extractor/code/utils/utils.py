import argparse
import requests
import shutil
import os
import glob
import json
import yaml
import pandas as pd
from utils.paths import path_file_running
import traceback
import pickle
import datetime
from utils.s3_communication import S3Communication
from pathlib import Path
from utils.paths import ProjectPaths
from utils.settings import Settings


def save_train_info(project_name, s3_usage=False, s3c_main: S3Communication = None, main_settings: Settings = None, 
                    s3_settings: Settings = None, project_paths: ProjectPaths = None):
    """
    This function stores all information of the training to a dictionary and saves it into a pickle file.
    Read it via:
    relevance_model = 'output'
    kpi_model = 'output'
    file_src_path = project_model_dir
    file_src_path = file_src_path + '/rel_text_' + relevance_model + '_kpi_text_' + kpi_model + '.pickle'
    with open(file_src_path, 'rb') as handle:
    b = pickle.load(handle)
    :param project_name: str
    return None
    """
    if s3_usage:
        # s3_settings = project_settings["s3_settings"]
        project_prefix = s3_settings.prefix + "/" + project_name + '/data'
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/kpi_mapping', str(project_paths.path_folder_source_mapping))
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/annotations', str(project_paths.path_folder_source_annotation))
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/pdfs/training', str(project_paths.path_folder_source_pdf))
    
    dir_train = {}
    dir_train.update({'project_name': project_name})
    # dir_train.update({'train_settings': project_settings})
    dir_train.update({'train_settings': main_settings})
    # dir_train.update({'pdfs_used': os.listdir(source_pdf)})
    dir_train.update({'pdfs_used': os.listdir(project_paths.path_folder_source_pdf)})
    first = True
    for filename in os.listdir(str(project_paths.path_folder_source_annotation)):
        if(filename[-5:]=='.xlsx'):
            if first:
                dir_train.update({'annotations': pd.read_excel(str(project_paths.path_folder_source_annotation) + r'/' + filename, engine='openpyxl') })
                first = False
    dir_train.update({'kpis': pd.read_csv(str(project_paths.path_folder_source_mapping) + '/kpi_mapping.csv')})
    
    # relevance_model = project_settings['train_relevance']['output_model_name']
    relevance_model = main_settings.train_relevance.output_model_name
    # kpi_model = project_settings['train_kpi']['output_model_name']
    kpi_model = main_settings.train_kpi.output_model_name

    name_out = str(project_paths.path_project_model_folder)
    name_out = name_out + '/SUMMARY_REL_' + relevance_model + '_KPI_' + kpi_model + '.pickle'
        
    with open(name_out, 'wb') as handle:
        pickle.dump(dir_train, handle, protocol=pickle.HIGHEST_PROTOCOL)
    if s3_usage:
        response_2 = s3c_main.upload_file_to_s3(filepath=name_out,
                      s3_prefix=str(Path(s3_settings.prefix) / project_name / 'models'),
                      s3_key='SUMMARY_REL_' + relevance_model + '_KPI_' + kpi_model + '.pickle')
    
    return None



def generate_text_3434(project_name, s3_usage, s3_settings, project_paths: ProjectPaths):
    """
    This function merges all infer relevance outputs into one large file, which is then 
    used to train the kpi extraction model.
    
    :param project_name: str, representing the project we currently work on
    :param s3_usage: boolean, if we use s3 as we then have to upload the new csv file to s3
    :param s3_settings: dictionary, containing information in case of s3 usage
    return None
    """
    if s3_usage:
        s3c_main = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
            aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
            aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
            s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
        )
        # Download infer relevance files
        prefix_rel_infer = str(Path(s3_settings['prefix']) / project_name / 'data' / 'output' / 'RELEVANCE' / 'Text')
        s3c_main.download_files_in_prefix_to_dir(prefix_rel_infer, str(project_paths.path_folder_relevance))
        
    with open(str(project_paths.path_folder_text_3434) + r"/text_3434.csv", "w") as file_out:
        very_first = True
        rel_inf_list = list(glob.iglob(str(project_paths.path_folder_relevance) + r'/*.csv'))
        if len(rel_inf_list) == 0:
            print("No relevance inference results found.")
            return False
        else:
            try:
                for filepath in rel_inf_list: 
                    print(filepath)
                    with open(filepath) as file_in:
                        first = True
                        for l in file_in:
                            if(very_first or not first):
                                file_out.write(l)
                            first = False
                        very_first = False
            except Exception:
                return False
    
    if s3_usage:
        s3c_interim = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings['interim_bucket']['s3_endpoint']),
            aws_access_key_id=os.getenv(s3_settings['interim_bucket']['s3_access_key']),
            aws_secret_access_key=os.getenv(s3_settings['interim_bucket']['s3_secret_key']),
            s3_bucket=os.getenv(s3_settings['interim_bucket']['s3_bucket_name']),
        )
        project_prefix_text3434 = str(Path(s3_settings['prefix']) / project_name / 'data' / 'interim' / 'ml')
        s3c_interim.upload_file_to_s3(filepath=str(project_paths.path_folder_text_3434) + r"/text_3434.csv", s3_prefix=project_prefix_text3434, s3_key='text_3434.csv')
    
    return True


def copy_file_without_overwrite(src_path, dest_path):
    for filename in os.listdir(src_path):
        # construct the src path and file name
        src_path_file_name = os.path.join(src_path, filename)
        # construct the dest path and file name
        dest_path_file_name = os.path.join(dest_path, filename)
        # test if the dest file exists, if false, do the copy, or else abort the copy operation.
        if not os.path.exists(dest_path_file_name):
            shutil.copyfile(src_path_file_name, dest_path_file_name)
    return True      

def link_files(source_dir, destination_dir):
    files = os.listdir(source_dir)
    for file in files:
        os.link(f"{source_dir}/{file}", f"{destination_dir}/{file}")
        

def link_extracted_files(src_ext, src_pdf, dest_ext):
    extracted_pdfs = [name[:-5] + ".pdf"  for name in os.listdir(src_ext)]
    for pdf in os.listdir(src_pdf):
        if pdf in extracted_pdfs:
            json_name = pdf[:-4] + ".json"
            # construct the src path and file name
            src_path_file_name = os.path.join(src_ext, json_name)
            # construct the dest path and file name
            dest_path_file_name = os.path.join(dest_ext, json_name)
            # test if the dest file exists, if false, do the copy, or else abort the copy operation.
            if not os.path.exists(dest_path_file_name):
                shutil.copyfile(src_path_file_name, dest_path_file_name)
    return True


