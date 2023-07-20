import argparse
import requests
import shutil
import os
import glob
import json
import yaml
import pandas as pd
import config_path
import traceback
import pickle
import datetime
from s3_communication import S3Communication
from pathlib import Path

FILE_RUNNING = config_path.NLP_DIR+r'/data/running'

project_settings = None
source_pdf = None
source_annotation = None
source_mapping = None
destination_pdf = None
destination_annotation = None
destination_mapping = None
destination_extraction = None
destination_curation = None
destination_training = None
destination_saved_models_relevance = None
destination_saved_models_inference = None
folder_text_3434 = None
folder_relevance = None

s3_usage = None
s3c_main = None
s3c_interim = None
project_prefix = None


def set_running():
     with open(FILE_RUNNING, 'w'):
          pass


def clear_running():
     try:
          os.unlink(FILE_RUNNING)
     except Exception as e:
          pass


def check_running():
     return os.path.exists(FILE_RUNNING)


def create_directory(directory_name):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def link_files(source_dir, destination_dir):
    files = os.listdir(source_dir)
    for file in files:
        os.link(f"{source_dir}/{file}", f"{destination_dir}/{file}")


def generate_text_3434(project_name, s3_usage, s3_settings):
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
        prefix_rel_infer = str(Path(s3_settings['prefix']) / project_name / 'output' / 'RELEVANCE' / 'Text')
        s3c_main.download_files_in_prefix_to_dir(prefix_rel_infer, str(folder_relevance))
        
    with open(folder_text_3434 + r"/text_3434.csv", "w") as file_out:
        very_first = True
        rel_inf_list = list(glob.iglob(folder_relevance + r'/*.csv'))
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
        s3c_interim.upload_file_to_s3(filepath=folder_text_3434 + r"/text_3434.csv", s3_prefix=project_prefix_text3434, s3_key='text_3434.csv')
    
    return True


def convert_xls_to_csv(project_name):
    """
    This function transforms the annotations.xlsx file into annotations.csv.
    
    :param project_name: str, representing the project we currently work on
    :param s3_usage: boolean, if we use s3 as we then have to upload the new csv file to s3
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
            #read_file = pd.read_excel(source_dir + r'/' + filename, sheet_name = 'data_ex_in_xls', engine='openpyxl')
            read_file = pd.read_excel(source_dir + r'/' + filename, engine='openpyxl') #only reads first sheet in excel file
            read_file.to_csv(dest_dir + r'/aggregated_annotation.csv', index = None, header=True)
            if s3_usage:
                s3c_interim.upload_files_in_dir_to_prefix(dest_dir, 
                                                  project_prefix + '/interim/ml/annotations')
            first = False         
    if(first):
        raise ValueError('No annotation excel sheet found')


def save_train_info(project_name, s3_usage=False, s3c_main=None, s3_settings=None):
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
        s3_settings = project_settings["s3_settings"]
        project_prefix = s3_settings['prefix'] + "/" + project_name + '/data'
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/kpi_mapping', source_mapping)
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/annotations', source_annotation)
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/pdfs/training', source_pdf)
    
    dir_train = {}
    dir_train.update({'project_name': project_name})
    dir_train.update({'train_settings': project_settings})
    dir_train.update({'pdfs_used': os.listdir(source_pdf)})
    first = True
    for filename in os.listdir(source_annotation):
        if(filename[-5:]=='.xlsx'):
            if first:
                dir_train.update({'annotations': pd.read_excel(source_annotation + r'/' + filename, engine='openpyxl') })
                first = False
    dir_train.update({'kpis': pd.read_csv(source_mapping + '/kpi_mapping.csv')})
    
    relevance_model = project_settings['train_relevance']['output_model_name']
    kpi_model = project_settings['train_kpi']['output_model_name']

    name_out = project_model_dir
    name_out = name_out + '/SUMMARY_REL_' + relevance_model + '_KPI_' + kpi_model + '.pickle'
        
    with open(name_out, 'wb') as handle:
        pickle.dump(dir_train, handle, protocol=pickle.HIGHEST_PROTOCOL)
    if s3_usage:
        response_2 = s3c_main.upload_file_to_s3(filepath=name_out,
                      s3_prefix=str(Path(s3_settings['prefix']) / project_name / 'models'),
                      s3_key='SUMMARY_REL_' + relevance_model + '_KPI_' + kpi_model + '.pickle')
    
    return None


def run_router(ext_port, infer_port, project_name,ext_ip='0.0.0.0',infer_ip='0.0.0.0'):
    """
    Router function
    It fist sends a command to the extraction server to beging extraction.
    If done successfully, it will send a commnad to the inference server to start inference.
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
    ext_resp = requests.get(f"http://{ext_ip}:{ext_port}/extract", params=payload)
    print(ext_resp.text)
    if ext_resp.status_code != 200:
        return False
    
    # Sending an execution request to the extraction server for curation
    ext_resp = requests.get(f"http://{ext_ip}:{ext_port}/curate", params=payload)
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
        train_resp = requests.get(f"http://{infer_ip}:{infer_port}/train_relevance", params=payload)
        print(train_resp.text)
        if train_resp.status_code != 200:
            return False
    else:
        print("No relevance training done. If you want to have a relevance training please set variable train under train_relevance to true.")
    
    if project_settings['train_kpi']['train']:
        # Requesting the inference server to start the relevance stage
        infer_resp = requests.get(f"http://{infer_ip}:{infer_port}/infer_relevance", params=payload)
        print(infer_resp.text)
        if infer_resp.status_code != 200:
            return False
        try:
            temp = generate_text_3434(project_name, project_settings['s3_usage'], project_settings['s3_settings'])
            if temp:
                print('text_3434 was generated without error.')
            else:
                print('text_3434 was not generated without error.')
        except Exception as e:
            print('Error while generating text_3434.')
            print(repr(e))
            print(traceback.format_exc())
        
        # Requesting the inference server to start the kpi extraction stage
        infer_resp_kpi = requests.get(f"http://{infer_ip}:{infer_port}/train_kpi", params=payload)
        print(infer_resp_kpi.text)
        if infer_resp_kpi.status_code != 200:
            return False
    else:
        print("No kpi training done. If you want to have a kpi training please set variable train under train_kpi to true.")
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


def main():
    global project_settings
    global source_pdf
    global source_annotation
    global source_mapping
    global destination_pdf
    global destination_annotation
    global destination_mapping
    global destination_extraction
    global destination_curation
    global destination_training
    global destination_saved_models_relevance
    global destination_saved_models_inference
    global project_model_dir
    global folder_text_3434
    global folder_relevance
    global s3_usage
    global s3c_main
    global s3c_interim
    global project_prefix

    if(check_running()):
        print("Another training or inference process is currently running.")
        return
        
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
    if(project_name is None or project_name==""):
        print("project name must not be empty")
        return

    s3_usage = args.s3_usage
    if s3_usage is None:
        s3_usage = input('Do you want to use S3? Type either Y or N.')
    if (s3_usage is None or str(s3_usage) not in ['Y', 'N']):
        print("Answer to S3 usage must by Y or N. Stop program. Please restart.")
        return None
    else:
        s3_usage = s3_usage == 'Y'

    project_data_dir = config_path.DATA_DIR + r'/' + project_name
    s3c_main = None 
    if s3_usage:
        # Opening s3 settings file
        s3_settings_path = config_path.DATA_DIR + r'/' + 's3_settings.yaml'        
        f = open(s3_settings_path, 'r')
        s3_settings = yaml.safe_load(f)
        f.close()
        project_prefix = s3_settings['prefix'] + "/" + project_name + '/data'
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
        settings_path = project_data_dir + "/settings.yaml"
        s3c_main.download_file_from_s3(filepath=settings_path,
                                  s3_prefix=project_prefix,
                                  s3_key='settings.yaml')

    # Opening YAML file
    f = open(project_data_dir + r'/settings.yaml', 'r')
    project_settings = yaml.safe_load(f)
    f.close()

    project_settings.update({'s3_usage': s3_usage})
    if s3_usage:
        project_settings.update({'s3_settings': s3_settings})
    
    project_model_dir = config_path.MODEL_DIR + r'/' + project_name
    ext_port = project_settings['general']['ext_port']
    infer_port = project_settings['general']['infer_port']
    ext_ip = project_settings['general']['ext_ip']
    infer_ip = project_settings['general']['infer_ip']
    relevance_training_output_model_name = project_settings['train_relevance']['output_model_name']
    kpi_inference_training_output_model_name = project_settings['train_kpi']['output_model_name']
    
    set_running()
    try:
        source_pdf = project_data_dir + r'/input/pdfs/training'
        source_annotation = project_data_dir + r'/input/annotations'
        source_mapping = project_data_dir + r'/input/kpi_mapping'
        destination_pdf = project_data_dir + r'/interim/pdfs/'
        destination_annotation = project_data_dir + r'/interim/ml/annotations/' 
        destination_mapping = project_data_dir + r'/interim/kpi_mapping/' 
        destination_extraction = project_data_dir + r'/interim/ml/extraction/' 
        destination_curation = project_data_dir + r'/interim/ml/curation/' 
        destination_training = project_data_dir + r'/interim/ml/training/'  
        destination_saved_models_relevance = project_model_dir + r'/RELEVANCE/Text'  + r'/' + relevance_training_output_model_name 
        destination_saved_models_inference = project_model_dir + r'/KPI_EXTRACTION/Text' + r'/' + kpi_inference_training_output_model_name 
        folder_text_3434 = project_data_dir + r'/interim/ml'
        folder_relevance = project_data_dir + r'/output/RELEVANCE/Text'

        create_directory(folder_text_3434)
        create_directory(destination_pdf)
        create_directory(destination_annotation)
        create_directory(destination_mapping)
        create_directory(destination_extraction)
        create_directory(destination_training)
        create_directory(destination_curation)
        if project_settings['train_relevance']['train']:
            create_directory(destination_saved_models_relevance)
        if project_settings['train_kpi']['train']:
            create_directory(destination_saved_models_inference)
        create_directory(folder_relevance)

        link_files(source_pdf,destination_pdf)
        link_files(source_annotation,destination_annotation)
        link_files(source_mapping,destination_mapping)
        if project_settings['extraction']['use_extractions']:
            source_extraction = project_data_dir + r'/output/TEXT_EXTRACTION'
            if os.path.exists(source_extraction):
                link_extracted_files(source_extraction, source_pdf, destination_extraction)
        
        end_to_end_response = run_router(ext_port, infer_port, project_name, ext_ip, infer_ip)
        
        if end_to_end_response:
            if project_settings['extraction']['store_extractions']:
                print("Finally we transfer the text extraction to the output folder")
                source_extraction_data = destination_extraction
                destination_extraction_data = project_data_dir + r'/output/TEXT_EXTRACTION'
                if s3_usage:
                    s3c_interim.download_files_in_prefix_to_dir(project_prefix + '/interim/ml/extraction', 
                                  source_extraction_data)
                    s3c_main.upload_files_in_dir_to_prefix(source_extraction_data, 
                                  project_prefix + '/output/TEXT_EXTRACTION')
                else:
                    os.makedirs(destination_extraction_data, exist_ok=True)
                    end_to_end_response = copy_file_without_overwrite(source_extraction_data, destination_extraction_data)

                
            if project_settings['general']['delete_interim_files']:
                create_directory(destination_pdf)
                create_directory(destination_mapping)
                create_directory(destination_annotation)
                create_directory(destination_extraction)
                create_directory(destination_training)
                create_directory(destination_curation)
                create_directory(folder_text_3434)
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

    clear_running()


if __name__ == "__main__":
    main()
