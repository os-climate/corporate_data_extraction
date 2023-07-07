"""
A gathering of utility functions applied
"""
import argparse
import shutil
import os
import glob
import json
import traceback
import yaml
import pandas as pd
import pickle
import requests
from config import get_config

config = get_config()


def check_running() -> bool:
     return os.path.exists(config.FILE_RUNNING)


def create_directory(directory_name: str):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def link_files(source_dir: str, destination_dir: str):
    files = os.listdir(source_dir)
    for file in files:
        os.link(f"{source_dir}/{file}", f"{destination_dir}/{file}")


def generate_text_3434(project_name: str):
     with open(folder_text_3434 + r"/text_3434.csv", "w") as file_out:
         very_first = True
         for filepath in glob.iglob(folder_relevance + r'/*.csv'): 
            print(filepath)
            with open(filepath) as file_in:
                first = True
                for l in file_in:
                    if(very_first or not first):
                        file_out.write(l)
                    first = False
                very_first = False


def set_running():
     with open(config.FILE_RUNNING, 'w'):
          pass


def clear_running():
     try:
          os.unlink(config.FILE_RUNNING)
     except Exception as e:
          pass
      
      
def convert_xls_to_csv(project_name: str):
    """
    This function transforms the annotations.xlsx file into annotations.csv.
    
    :param project_name: str, representing the project we currently work on
    :param s3_usage: boolean, if we use s3 as we then have to upload the new 
    csv file to s3
    :param s3_settings: dictionary, containing information in case of s3 usage
    return None
    """
    source_dir = source_annotation
    dest_dir = destination_annotation
    s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/annotations', 
                                        source_dir)
    first = True
    for filename in os.listdir(source_dir):
        if(filename[-5:]=='.xlsx'):
            if(not first):
                raise ValueError('More than one excel sheet found')
            print('Converting ' + filename + ' to csv-format')
            #read_file = pd.read_excel(source_dir + r'/' + filename, 
            # sheet_name = 'data_ex_in_xls', engine='openpyxl')
            read_file = pd.read_excel(source_dir + r'/' + filename, 
                                      engine='openpyxl') #only reads first 
                                                         #sheet in excel file
            read_file.to_csv(dest_dir + r'/aggregated_annotation.csv', 
                             index = None, header=True)
            if s3_usage:
                s3c_interim.upload_files_in_dir_to_prefix(dest_dir, 
                                                  project_prefix + 
                                                  '/interim/ml/annotations')
            first = False         
    if(first):
        raise ValueError('No annotation excel sheet found')


def save_train_info(project_name: str):
    """
    This function stores all information of the training to a dictionary and 
    saves it into a pickle file.
    Read it via:
    relevance_model = 'output'
    kpi_model = 'output'
    cons_date = '20220422132203'
    file_src_path = project_model_dir
    file_src_path = file_src_path + '/rel_text_' + relevance_model + 
    '_kpi_text_' + kpi_model + '_' + cons_date + '.pickle'
    with open(file_src_path, 'rb') as handle:
    b = pickle.load(handle)
    :param project_name: str
    return None
    """
    dir_train = {}
    dir_train.update({'project_name': project_name})
    dir_train.update({'train_settings': project_settings})
    dir_train.update({'pdfs_used': os.listdir(source_pdf)})
    first = True
    for filename in os.listdir(source_annotation):
        if(filename[-5:]=='.xlsx'):
            if first:
                dir_train.update({'annotations': pd.read_excel(
                    source_annotation + r'/' + filename, engine='openpyxl') })
                first = False
    dir_train.update({'kpis': pd.read_csv(source_mapping + '/kpi_mapping.csv')})

    relevance_model = project_settings['train_relevance']['output_model_name']
    kpi_model = project_settings['train_kpi']['output_model_name']

    name_out = project_model_dir
    name_out = name_out + '/rel_text_' + relevance_model + \
        '_kpi_text_' + kpi_model + '.pickle'
        
    with open(name_out, 'wb') as handle:
        pickle.dump(dir_train, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return None


def run_router(ext_port: int, infer_port: int, project_name: str, 
               ext_ip: str ='0.0.0.0', infer_ip: str ='0.0.0.0') -> bool:
    """
    Router function
    It first sends a command to the extraction server to beging extraction.
    If done successfully, it will send a commnad to the inference server to 
    start inference.
    :param ext_port (int): The port that the extraction server is listening on
    :param infer_port (int): The port that the inference server is listening on
    :param ext_ip (int): The ip that the extraction server is listening on
    :param infer_ip (int): The ip that the inference server is listening on
    :return: A boolean, indicating success
    """

    convert_xls_to_csv(project_name)

    # Check if the extraction server is live
    ext_live = requests.get(f"http://{ext_ip}:{ext_port}/liveness")
    if ext_live.status_code == 200:
        print("Extraction server is up. Proceeding to extraction.")
    else:
        print("Extraction server is not responding.")
        return False

    payload = {'project_name': project_name, 'mode': 'train'}
    payload.update(project_settings)
    payload = {'payload': json.dumps(payload)}

    # Sending an execution request to the extraction server for extraction
    ext_resp = requests.get(
        f"http://{ext_ip}:{ext_port}/extract", params=payload)
    print(ext_resp.text)
    if ext_resp.status_code != 200:
        return False

    # Sending an execution request to the extraction server for curation
    ext_resp = requests.get(
        f"http://{ext_ip}:{ext_port}/curate", params=payload)
    print(ext_resp.text)
    if ext_resp.status_code != 200:
        return False

    # Check if the inference server is live
    infer_live = requests.get(f"http://{infer_ip}:{infer_port}/liveness")
    if infer_live.status_code == 200:
        print("Inference server is up. Proceeding to Inference.")
    else:
        print("Inference server is not responding.")
        return False
    
    if project_settings['train_relevance']['train']:
        print("Relevance training will be started.")
        # Requesting the inference server to start the relevance stage
        train_resp = requests.get(
            f"http://{infer_ip}:{infer_port}/train_relevance", params=payload)
        print(train_resp.text)
        if train_resp.status_code != 200:
            return False
    else:
        print("No relevance training done. If you want to have a relevance \
            training please set variable train under train_relevance to true.")
    
    if project_settings['train_kpi']['train']:
        # Requesting the inference server to start the relevance stage
        infer_resp = requests.get(
            f"http://{infer_ip}:{infer_port}/infer_relevance", params=payload)
        print(infer_resp.text)
        if infer_resp.status_code != 200:
            return False
        try:
            generate_text_3434(project_name)
            print('text_3434 was generated without error.')
        except Exception as e:
            print('Error while generating text_3434.')
            print(repr(e))
            print(traceback.format_exc())
        
        # Requesting the inference server to start the kpi extraction stage
        infer_resp_kpi = requests.get(
            f"http://{infer_ip}:{infer_port}/train_kpi", params=payload)
        print(infer_resp_kpi.text)
        if infer_resp_kpi.status_code != 200:
            return False
    else:
        print("No kpi training done. If you want to have a kpi training please \
            set variable train under train_kpi to true.")
    return True


def copy_file_without_overwrite(src_path: str, dest_path: str) -> bool:
    for filename in os.listdir(src_path):
        # construct the src path and file name
        src_path_file_name = os.path.join(src_path, filename)
        # construct the dest path and file name
        dest_path_file_name = os.path.join(dest_path, filename)
        # test if the dest file exists, if false, do the copy, or else abort
        # the copy operation.
        if not os.path.exists(dest_path_file_name):
            shutil.copyfile(src_path_file_name, dest_path_file_name)
    return True


def link_extracted_files(src_ext: str, src_pdf: str, dest_ext: str) -> bool:
    extracted_pdfs = [name[:-5] + ".pdf"  for name in os.listdir(src_ext)]
    for pdf in os.listdir(src_pdf):
        if pdf in extracted_pdfs:
            json_name = pdf[:-4] + ".json"
            # construct the src path and file name
            src_path_file_name = os.path.join(src_ext, json_name)
            # construct the dest path and file name
            dest_path_file_name = os.path.join(dest_ext, json_name)
            # test if the dest file exists, if false, do the copy, or else 
            # abort the copy operation.
            if not os.path.exists(dest_path_file_name):
                shutil.copyfile(src_path_file_name, dest_path_file_name)
    return True