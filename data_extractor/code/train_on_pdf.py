import argparse
import os
import traceback
import yaml
from config import get_config
from s3_communication import S3Communication
from utils import check_running, create_directory, link_files, set_running, \
    clear_running, save_train_info, run_router, link_extracted_files, \
    copy_file_without_overwrite

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


def main():
    config = get_config()
    
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
        print("Answer to S3 usage must by Y or N. Stop program. \
            Please restart.")
        return None
    else:
        s3_usage = s3_usage == 'Y'

    project_data_dir = config.DATA_DIR + r'/' + project_name

    if s3_usage:
        # Opening s3 settings file
        s3_settings_path = config.DATA_DIR + r'/' + 's3_settings.yaml'        
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
    
    project_model_dir = config.MODEL_DIR + r'/' + project_name
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
            if end_to_end_response:
                save_train_info(project_name)
                print("End-to-end inference complete")

    except Exception as e:
        print('Process failed to run. Reason: ' + str(repr(e)) + traceback.format_exc())

    clear_running()


if __name__ == "__main__":
    main()
