import argparse
import requests
import os
import utils.config_path as config_path
import json
import yaml
import csv
import time
import traceback
import shutil
from s3_communication import S3Communication
import pandas as pd

path_file_running = config_path.NLP_DIR+r'/data/running'

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


def set_running():
    with open(path_file_running, 'w'):
        pass


def clear_running():
    try:
        os.unlink(path_file_running)
    except Exception as e:
        pass


def check_running():
    return os.path.exists(path_file_running)


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
        try:
            os.unlink(f"{destination_dir}/{file}")
        except Exception:
            pass
        os.link(f"{source_dir}/{file}", f"{destination_dir}/{file}")


def copy_files_without_overwrite(src_path, dest_path):
    for filename in os.listdir(src_path):    
        # construct the src path and file name
        src_path_file_name = os.path.join(src_path, filename)
        # construct the dest path and file name
        dest_path_file_name = os.path.join(dest_path, filename)
        # test if the dest file exists, if false, do the copy, or else abort the copy operation.
        if not os.path.exists(dest_path_file_name):
            shutil.copyfile(src_path_file_name, dest_path_file_name)
    return None


def link_extracted_files(src_ext, src_pdf, dest_ext):
    extracted_pdfs = [name[:-5] + ".pdf" for name in os.listdir(src_ext)]
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


def convert_xls_to_csv(project_name, s3_usage, s3_settings):
    """
    This function transforms the annotations.xlsx file into annotations.csv.
    
    :param project_name: str, representing the project we currently work on
    :param s3_usage: boolean, if we use s3 as we then have to upload the new csv file to s3
    :param s3_settings: dictionary, containing information in case of s3 usage
    return None
    """
    source_dir = source_annotation
    dest_dir = destination_annotation
    if s3_usage:
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
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/annotations', 
                                                 source_dir)
    first = True
    for filename in os.listdir(source_dir):
        if filename[-5:] == '.xlsx':
            if not first:
                raise ValueError('More than one excel sheet found')
            print('Converting ' + filename + ' to csv-format')
            # only reads first sheet in excel file
            read_file = pd.read_excel(source_dir + r'/' + filename, engine='openpyxl')
            read_file.to_csv(dest_dir + r'/aggregated_annotation.csv', index=None, header=True)
            if s3_usage:
                s3c_interim.upload_files_in_dir_to_prefix(dest_dir,  project_prefix + '/interim/ml/annotations')
            first = False         
    if first:
        raise ValueError('No annotation excel sheet found')


def run_router_ml(ext_port, infer_port, project_name, ext_ip='0.0.0.0', infer_ip='0.0.0.0'):
    """
    Router function
    It fist sends a command to the extraction server to begin extraction.
    If done successfully, it will send a command to the inference server to start inference.
    :param ext_port: int: The port that the extraction server is listening on
    :param infer_port: int: The port that the inference server is listening on
    :param project_name: str: The name of the project
    :param ext_ip: int: The ip that the extraction server is listening on
    :param infer_ip: int: The ip that the inference server is listening on
    :return: A boolean, indicating success
    """
    
    convert_xls_to_csv(project_name, project_settings['s3_usage'], project_settings['s3_settings'])
    
    # Check if the extraction server is live
    ext_live = requests.get(f"http://{ext_ip}:{ext_port}/liveness")
    if ext_live.status_code == 200:
        print("Extraction server is up. Proceeding to extraction.")
    else:
        print("Extraction server is not responding.")
        return False
        
    payload = {'project_name': project_name, 'mode': 'infer'}
    payload.update(project_settings)
    payload = {'payload': json.dumps(payload)} 

    # Sending an execution request to the extraction server for extraction
    ext_resp = requests.get(f"http://{ext_ip}:{ext_port}/extract", params=payload)
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

    # Requesting the inference server to start the relevance stage
    infer_resp = requests.get(f"http://{infer_ip}:{infer_port}/infer_relevance", params=payload)
    print(infer_resp.text)
    if infer_resp.status_code != 200:
        return False

    # Requesting the inference server to start the kpi extraction stage
    infer_resp_kpi = requests.get(f"http://{infer_ip}:{infer_port}/infer_kpi", params=payload)
    print(infer_resp_kpi.text)
    if infer_resp_kpi.status_code != 200:
        return False
    return True


def run_router_rb(raw_pdf_folder, working_folder, output_folder, project_name, verbosity, use_docker, port, ip,
                  s3_usage, s3_settings):
    if use_docker:
        payload = {'project_name': project_name, 'verbosity': str(verbosity)}
        if s3_usage:
            payload.update({'s3_usage': s3_usage})
            payload.update({'s3_settings': s3_settings})
        payload = {'payload': json.dumps(payload)}
        rb_response = requests.get(f"http://{ip}:{port}/run", params=payload)
        print(rb_response.text)
        if rb_response.status_code != 200:
            return False
    else:
        cmd = config_path.PYTHON_EXECUTABLE + ' rule_based_pipeline/rule_based_pipeline/main.py' + \
                 ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
                 ' --working_folder "' + working_folder + '"' +    \
                 ' --output_folder "' + output_folder + '"' +     \
                 ' --verbosity ' + str(verbosity)
        print("Running command: " + cmd)
        os.system(cmd)
    return True 


def set_xy_ml(project_name, raw_pdf_folder, working_folder, pdf_name, csv_name, output_folder, verbosity, use_docker,
              port, ip, s3_usage, s3_settings):
    if use_docker:
        payload = {'project_name': project_name,
                   'pdf_name': pdf_name,
                   'csv_name': csv_name,
                   'verbosity': str(verbosity)}
        if s3_usage:
            payload.update({'s3_usage': s3_usage})
            payload.update({'s3_settings': s3_settings})
        payload = {'payload': json.dumps(payload)}
        rb_xy_extract_response = requests.get(f"http://{ip}:{port}/run_xy_ml", params=payload)
        print(rb_xy_extract_response.text)
        if rb_xy_extract_response.status_code != 200:
            return False
    else:
        cmd = config_path.PYTHON_EXECUTABLE + ' rule_based_pipeline/rule_based_pipeline/main_find_xy.py' + \
                 ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
                 ' --working_folder "' + working_folder + '"' +    \
                 ' --pdf_name "' + pdf_name + '"' +     \
                 ' --csv_name "' + csv_name + '"' +     \
                 ' --output_folder "' + output_folder + '"' +     \
                 ' --verbosity ' + str(verbosity)
        print("Running command: " + cmd)
    
    return True 


def get_current_run_id():
    return int(time.time())
    

def try_int(val, default):
    try:
        return int(float(val))
    except Exception:
        pass
    return default


def join_output(project_name, pdf_folder, rb_output_folder, ml_output_folder, output_folder, use_docker, work_dir_rb,
                verbosity, port, ip, run_id, s3_usage, s3_settings):
    print("Joining output . . . ")
    # ML header:  ,pdf_name,kpi,kpi_id,answer,page,paragraph,source,score,no_ans_score,no_answer_score_plus_boost
    # RB header:  "KPI_ID","KPI_NAME","SRC_FILE","PAGE_NUM","ITEM_IDS","POS_X","POS_Y","RAW_TXT",
    # "YEAR","VALUE","SCORE","UNIT","MATCH_TYPE"
    output_header = ["METHOD", "PDF_NAME", "KPI_ID", "KPI_NAME", "KPI_DESC",
                     "ANSWER_RAW", "ANSWER", "PAGE", "PARAGRAPH", "PARAGRAPH_RELEVANCE_SCORE", "POS_X", "POS_Y",
                     "KPI_SOURCE", "SCORE", "NO_ANS_SCORE", "SCORE_PLUS_BOOST", "KPI_YEAR", "UNIT_RAW", "UNIT"]
    for filename in os.listdir(pdf_folder):
        print(filename)
        with open(output_folder + r'/' + str(run_id) + r'_' + filename + r'.csv', 'w',
                  encoding='UTF8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(output_header)
            
            rb_filename = rb_output_folder + r'/' + filename + '.csv'
            ml_filename = ml_output_folder + r'/' + filename[:len(filename)-4] + '_predictions_kpi.csv'
            # Read RB:
            try:
                with open(rb_filename, 'r') as f:
                    csv_file = csv.DictReader(f)
                    for row in csv_file:
                        d = dict(row)
                        # TODO: Use UNIT_RAW/UNIT, once implemented in RB solution
                        data = ["RB", d["SRC_FILE"], d["KPI_ID"], d["KPI_NAME"], "", d["RAW_TXT"],
                                d["VALUE"], d["PAGE_NUM"], "", "", d["POS_X"], d["POS_Y"],
                                d["MATCH_TYPE"], d["SCORE"], "", "", d["YEAR"], d["UNIT"], d["UNIT"]]
                        writer.writerow(data)
            except IOError:
                pass # RB not executed
            # Read ML:
            try:
                with open(ml_filename, 'r') as f:
                    csv_file = csv.DictReader(f)
                    for row in csv_file:
                        d = dict(row)
                        data = ["ML", d["pdf_name"] + r".pdf", "", "", d["kpi"], d["answer"], d["answer"],
                                str(try_int(d["page"], -2)+1), d["paragraph"], d["paragraph_relevance_score"], "", "",
                                d["source"], d["score"], d["no_ans_score"], d["no_answer_score_plus_boost"], "", "", ""]
                        writer.writerow(data)
            except IOError:
                pass # ML not executed
        csv_name = str(run_id) + r'_' + filename + r'.csv'
        if csv_name in os.listdir(output_folder):
            if s3_usage:
                project_prefix = s3_settings['prefix'] + "/" + project_name + '/data'
                s3c_main = S3Communication(
                        s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
                        aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
                        aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
                        s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
                )
                s3c_main.upload_file_to_s3(filepath=output_folder + r'/' + csv_name,
                                           s3_prefix=project_prefix + '/output/KPI_EXTRACTION/joined_ml_rb',
                                           s3_key=csv_name)
            set_xy_ml(project_name=project_name, raw_pdf_folder=pdf_folder, working_folder=work_dir_rb,
                      pdf_name=filename, csv_name=csv_name, output_folder=output_folder, verbosity=verbosity,
                      use_docker=use_docker, port=port, ip=ip, s3_usage=s3_usage, s3_settings=s3_settings)
        else:
            print(f'File {csv_name} not in the output and hence we are not able to detect x, '
                  f'y coordinates for the ML solution output.')
    if s3_usage:
        create_directory(pdf_folder)
        create_directory(rb_output_folder)
        create_directory(ml_output_folder)
        create_directory(output_folder)


def run_db_export(project_name, settings, run_id):
    cmd = config_path.PYTHON_EXECUTABLE + ' dataload/db_export.py' + \
             ' --project_name "' + project_name + '"' +    \
             ' --run_id "' + str(run_id) + '"'
    print("Running command: " + cmd)
    os.system(cmd)
    return True 


def main():
    global project_settings
    global source_annotation
    global destination_annotation
    
    if check_running():
        print("Another training or inference process is currently running.")
        return
        
    parser = argparse.ArgumentParser(description='End-to-end inference')
    
    # Add the arguments
    parser.add_argument('--project_name',
                        type=str,
                        default=None,
                        help='Name of the Project')
                    
    parser.add_argument('--mode',
                        type=str,
                        default='both',
                        help='Inference Mode (RB, ML, both, or none - for just doing postprocessing)')
    
    parser.add_argument('--s3_usage',
                        type=str,
                        default=None,
                        help='Do you want to use S3? Type either Y or N.')
    
    args = parser.parse_args()
    project_name = args.project_name
    mode = args.mode
    
    if mode not in ('RB', 'ML', 'both', 'none'):
        print("Illegal mode specified. Mode must be either RB, ML, both or none")
        return
    
    if project_name is None:
        project_name = input("What is the project name? ")
    if project_name is None or project_name == "":
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
    
    project_data_dir = config_path.DATA_DIR + r'/' + project_name
    create_directory(project_data_dir)
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

    ext_port = project_settings['general']['ext_port']
    infer_port = project_settings['general']['infer_port']
    rb_port = project_settings['general']['rb_port']

    ext_ip = project_settings['general']['ext_ip']
    infer_ip = project_settings['general']['infer_ip']
    rb_ip = project_settings['general']['rb_ip']

    enable_db_export = project_settings['data_export']['enable_db_export']
    rb_verbosity = int(project_settings['rule_based']['verbosity'])
    rb_use_docker = project_settings['rule_based']['use_docker']
  
    set_running()
    try:
        # Source folders
        source_pdf = project_data_dir + r'/input/pdfs/inference'
        destination_pdf = project_data_dir + r'/interim/pdfs/'
        source_mapping = project_data_dir + r'/input/kpi_mapping'
        source_annotation = project_data_dir + r'/input/annotations'
        destination_annotation = project_data_dir + r'/interim/ml/annotations/' 

        # Interim folders
        destination_mapping = project_data_dir + r'/interim/kpi_mapping/'
        destination_ml_extraction = project_data_dir + r'/interim/ml/extraction/'
        destination_rb_workdir = project_data_dir + r'/interim/rb/work'
        destination_rb_infer = project_data_dir + r'/output/KPI_EXTRACTION/rb'
        destination_ml_infer = project_data_dir + r'/output/KPI_EXTRACTION/ml/Text'

        # Output folders
        destination_output = project_data_dir + r'/output/KPI_EXTRACTION/joined_ml_rb'

        create_directory(source_pdf)
        create_directory(source_mapping)
        create_directory(destination_pdf)
        create_directory(destination_mapping)
        create_directory(destination_ml_extraction)
        create_directory(destination_annotation)
        if mode != 'none':
            create_directory(destination_rb_infer)
            create_directory(destination_ml_infer)        
        os.makedirs(destination_rb_workdir, exist_ok=True)
        os.makedirs(destination_output, exist_ok=True)

        link_files(source_pdf, destination_pdf)
        link_files(source_mapping, destination_mapping)
        if project_settings['extraction']['use_extractions']:
            source_extraction = project_data_dir + r'/output/TEXT_EXTRACTION'
            if os.path.exists(source_extraction):
                link_extracted_files(source_extraction, source_pdf, destination_ml_extraction)
            
        end_to_end_response = True
        
        if mode in ('RB', 'both'):
            print("Executing RB solution . . . ")
            end_to_end_response = end_to_end_response and  \
                run_router_rb(raw_pdf_folder=destination_pdf,
                              working_folder=destination_rb_workdir,
                              output_folder=destination_rb_infer,
                              project_name=project_name,
                              verbosity=rb_verbosity,
                              use_docker=rb_use_docker,
                              ip=rb_ip,
                              port=rb_port,
                              s3_usage=s3_usage,
                              s3_settings=s3_settings)
            if s3_usage:
                # Download inference output
                s3c_main.download_files_in_prefix_to_dir(project_prefix + '/output/KPI_EXTRACTION/rb', 
                                                         destination_rb_infer)
        
        if mode in ('ML', 'both'):
            print("Executing ML solution . . . ")
            end_to_end_response = end_to_end_response and \
                                  run_router_ml(ext_port, infer_port, project_name, ext_ip, infer_ip)
            if s3_usage:
                # Download inference output
                s3c_main.download_files_in_prefix_to_dir(project_prefix + '/output/KPI_EXTRACTION/ml/Text', 
                                                         destination_ml_infer)

        if end_to_end_response:
            run_id = get_current_run_id()
            if s3_usage:
                # Download pdf's to folder
                s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/pdfs/inference', 
                                                         destination_pdf)
            
            join_output(project_name=project_name,
                        pdf_folder=destination_pdf,
                        rb_output_folder=destination_rb_infer,
                        ml_output_folder=destination_ml_infer,
                        output_folder=destination_output,
                        use_docker=rb_use_docker,
                        work_dir_rb=destination_rb_workdir,
                        verbosity=rb_verbosity,
                        port=rb_port,
                        ip=rb_ip,
                        run_id=run_id,
                        s3_usage=s3_usage,
                        s3_settings=s3_settings)
            if enable_db_export:
                print("Exporting output to database . . . ")
                run_db_export(project_name, project_settings['data_export'], run_id)
            if project_settings['extraction']['store_extractions']:
                print("Finally we transfer the text extraction to the output folder.")
                source_extraction_data = destination_ml_extraction
                destination_extraction_data = project_data_dir + r'/output/TEXT_EXTRACTION'
                if s3_usage:
                    s3c_interim.download_files_in_prefix_to_dir(project_prefix + '/interim/ml/extraction', 
                                                                source_extraction_data)
                    s3c_main.upload_files_in_dir_to_prefix(source_extraction_data, 
                                                           project_prefix + '/output/TEXT_EXTRACTION')
                os.makedirs(destination_extraction_data, exist_ok=True)
                copy_files_without_overwrite(source_extraction_data, destination_extraction_data)
            if project_settings['general']['delete_interim_files']:
                create_directory(destination_ml_extraction)
                create_directory(destination_rb_workdir)
                create_directory(destination_pdf)
                create_directory(destination_mapping)
                if s3_usage:
                    # Show only objects which satisfy our prefix
                    my_bucket = s3c_interim.s3_resource.Bucket(name=s3c_interim.bucket)
                    for objects in my_bucket.objects.filter(Prefix=project_prefix+'/interim'):
                        _ = objects.delete()
            if end_to_end_response:
                print("End-to-end inference complete")
    
    except Exception as e:
        print('Process failed to run. Reason:' + str(repr(e)) + traceback.format_exc())

    clear_running()


if __name__ == "__main__":
    main()