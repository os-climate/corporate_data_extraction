import argparse
import requests
import os
import config_path
import json
import yaml
import csv
import time
import traceback
import shutil

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
    try:
        shutil.rmtree(directory_name)
    except:
        pass
    os.makedirs(directory_name, exist_ok=True)


def link_files(source_dir, destination_dir):
    files = os.listdir(source_dir)
    for file in files:
        try:
            os.unlink(f"{destination_dir}/{file}")
        except:
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


def run_router_ml(ext_port, infer_port, project_name, ext_ip='0.0.0.0', infer_ip='0.0.0.0'):
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

    # Sending an execution request to the extraction server
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
    

def run_router_rb(raw_pdf_folder, working_folder, output_folder, project_name, verbosity, use_docker, rb_port, rb_ip):
    if(use_docker):
        payload = {'project_name': project_name, 'verbosity': str(verbosity)}
        rb_response = requests.get(f"http://{rb_ip}:{rb_port}/run", params=payload)
        print(rb_response.text)
        if rb_response.status_code != 200:
            return False
    else:
        cmd = config_path.PYTHON_EXECUTABLE + ' rule_based_pipeline/rule_based_pipeline/main.py' + \
                 ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
                 ' --working_folder "' + working_folder + '"' +    \
                 ' --output_folder "' + output_folder + '"'  +     \
                 ' --verbosity ' + str(verbosity)
        print("Running command: " + cmd)
        os.system(cmd)
    return True 


def set_xy_ml(project_name, raw_pdf_folder, working_folder, pdf_name, csv_name, output_folder, verbosity, use_docker, rb_port, rb_ip):
    if(use_docker):
        payload = {'project_name': project_name,
                   'pdf_name': pdf_name,
                   'csv_name': csv_name,
                   'verbosity': str(verbosity)}
        rb_xy_extract_response = requests.get(f"http://{rb_ip}:{rb_port}/run_xy_ml", params=payload)
        print(rb_xy_extract_response.text)
        if rb_xy_extract_response.status_code != 200:
            return False
    else:
        cmd = config_path.PYTHON_EXECUTABLE + ' rule_based_pipeline/rule_based_pipeline/main_find_xy.py' + \
                 ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
                 ' --working_folder "' + working_folder + '"' +    \
                 ' --pdf_name "' + pdf_name + '"'  +     \
                 ' --csv_name "' + csv_name + '"'  +     \
                 ' --output_folder "' + output_folder + '"'  +     \
                 ' --verbosity ' + str(verbosity)
        print("Running command: " + cmd)
    
    return True 


def get_current_run_id():
    return int(time.time())


def try_int(val, default):
    try:
        return int(float(val))
    except:
        pass
    return default


def join_output(project_name, pdf_folder, rb_output_folder, ml_output_folder, output_folder, use_docker, work_dir_rb, verbosity, rb_port, rb_ip, run_id):
    print("Joining output . . . ")
    # ML header:  ,pdf_name,kpi,kpi_id,answer,page,paragraph,source,score,no_ans_score,no_answer_score_plus_boost
    # RB header:  "KPI_ID","KPI_NAME","SRC_FILE","PAGE_NUM","ITEM_IDS","POS_X","POS_Y","RAW_TXT","YEAR","VALUE","SCORE","UNIT","MATCH_TYPE"
    output_header = ["METHOD", "PDF_NAME", "KPI_ID", "KPI_NAME", "KPI_DESC", \
                     "ANSWER_RAW", "ANSWER", "PAGE", "PARAGRAPH", "PARAGRAPH_RELEVANCE_SCORE", "POS_X", "POS_Y", \
                     "KPI_SOURCE", "SCORE", "NO_ANS_SCORE", "SCORE_PLUS_BOOST", "KPI_YEAR", "UNIT_RAW", "UNIT"]
    for filename in os.listdir(pdf_folder):
        print(filename)
        with open(output_folder + r'/' + str(run_id) + r'_' + filename + r'.csv', 'w', encoding='UTF8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(output_header)
            
            rb_filename = rb_output_folder + r'/' + filename + '.csv'
            ml_filename = ml_output_folder + r'/' + filename[:len(filename)-4] + '_predictions_kpi.csv'
            # Read RB:
            #print("ml=" + ml_filename)
            try:
                #print(rb_filename)
                with open(rb_filename, 'r') as f:
                    #print("open")
                    csv_file = csv.DictReader(f)
                    for row in csv_file:
                        d = dict(row)
                        data = ["RB", d["SRC_FILE"], d["KPI_ID"], d["KPI_NAME"], "", d["RAW_TXT"], d["VALUE"], d["PAGE_NUM"], "", "", d["POS_X"], d["POS_Y"], \
                             d["MATCH_TYPE"], d["SCORE"], "", "", d["YEAR"], d["UNIT"], d["UNIT"]] #TODO: Use UNIT_RAW/UNIT, once implemented in RB solution
                        writer.writerow(data)
            except IOError:
                pass # RB not executed
            # Read ML:
            try:
                #print(ml_filename)
                with open(ml_filename, 'r') as f:
                    #print("open")
                    csv_file = csv.DictReader(f)
                    for row in csv_file:
                        d = dict(row)
                        data = ["ML", d["pdf_name"] + r".pdf", "", "", d["kpi"], d["answer"], d["answer"], \
                             str(try_int(d["page"], -2)+1), d["paragraph"], d["paragraph_relevance_score"], "", "", \
                             d["source"], d["score"], d["no_ans_score"], d["no_answer_score_plus_boost"], "", "", ""]
                        writer.writerow(data)
            except IOError:
                pass # ML not executed
        csv_name = str(run_id) + r'_' + filename + r'.csv'
        if csv_name in os.listdir(output_folder):
            set_xy_ml(project_name=project_name, raw_pdf_folder=pdf_folder, working_folder=work_dir_rb, pdf_name=filename, 
                    csv_name=csv_name, output_folder=output_folder, verbosity=verbosity, use_docker=use_docker, rb_port=rb_port, rb_ip=rb_ip)
        else:
            print(f'File {csv_name} not in the output and hence we are not able to detect x, y coordinates for the ML solution output.')


def run_db_export(project_name, settings, run_id):
    cmd = config_path.PYTHON_EXECUTABLE + ' dataload/db_export.py' + \
             ' --project_name "' + project_name + '"' +    \
             ' --run_id "' + str(run_id) + '"'
    print("Running command: " + cmd)
    os.system(cmd)
    return True 


def main():
    global project_settings

    if(check_running()):
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
                    
    args = parser.parse_args()
    project_name = args.project_name
    mode = args.mode
    
    if(mode not in ('RB', 'ML', 'both', 'none')):
        print("Illegal mode specified. Mode must be either RB, ML, both or none")
        return
    
    if project_name is None:
        project_name = input("What is the project name? ")
    if(project_name is None or project_name==""):
        print("project name must not be empty")
        return           
      
    project_data_dir = config_path.DATA_DIR + r'/' + project_name
    project_model_dir = config_path.MODEL_DIR + r'/' + project_name
    
    # Opening YAML file
    f = open(project_data_dir + r'/settings.yaml', 'r')
    project_settings = yaml.safe_load(f)
    f.close()   

    ext_port = project_settings['general']['ext_port']
    infer_port = project_settings['general']['infer_port']
    rb_port = project_settings['general']['rb_port']
    ext_ip = project_settings['general']['ext_ip']
    infer_ip = project_settings['general']['infer_ip']
    rb_ip = project_settings['general']['rb_ip']

    enable_db_export = project_settings['data_export']['enable_db_export']
    rb_verbosity =  int(project_settings['rule_based']['verbosity'])
    rb_use_docker =  project_settings['rule_based']['use_docker']
  
    set_running()
    try:
        # Source folders
        source_pdf = project_data_dir + r'/input/pdfs/inference'
        destination_pdf = project_data_dir + r'/interim/pdfs/'
        source_mapping = project_data_dir + r'/input/kpi_mapping'

        # Interim folders
        destination_mapping = project_data_dir + r'/interim/kpi_mapping/'
        destination_ml_extraction = project_data_dir + r'/interim/ml/extraction/'
        #destination_saved_models_relevance = project_model_dir + r'/RELEVANCE/Text'  + r'/' + project_settings['train_relevance']['output_model_name']
        #destination_saved_models_inference = project_model_dir + r'/KPI_EXTRACTION/Text' + r'/' + project_settings['kpi_inference_training']['output_model_name'] 
        destination_rb_workdir  = project_data_dir + r'/interim/rb/work'
        destination_rb_infer = project_data_dir + r'/output/KPI_EXTRACTION/rb'
        destination_ml_infer = project_data_dir + r'/output/KPI_EXTRACTION/ml/Text'

        # Output folders
        destination_output = project_data_dir + r'/output/KPI_EXTRACTION'        
        create_directory(destination_pdf)
        create_directory(destination_mapping)
        create_directory(destination_ml_extraction)
        if(mode != 'none'):
            create_directory(destination_rb_infer)
            create_directory(destination_ml_infer)        
        os.makedirs(destination_rb_workdir, exist_ok=True)
        os.makedirs(destination_output, exist_ok=True)
        
        link_files(source_pdf,destination_pdf)        
        link_files(source_mapping,destination_mapping)
        if project_settings['extraction']['use_extractions']:
            source_extraction = project_data_dir + r'/output/TEXT_EXTRACTION'
            if os.path.exists(source_extraction):
                link_extracted_files(source_extraction, source_pdf, destination_ml_extraction)
            
        end_to_end_response = True
        
        if(mode in ('RB', 'both')):
            print("Executing RB solution . . . ")
            end_to_end_response = end_to_end_response and  \
                run_router_rb(raw_pdf_folder=destination_pdf, \
                              working_folder=destination_rb_workdir, \
                              output_folder=destination_rb_infer, \
                              project_name=project_name, \
                              verbosity=rb_verbosity, \
                              use_docker=rb_use_docker, \
                              rb_port=rb_port, \
                              rb_ip=rb_ip)
        
        if(mode in ('ML', 'both')):
            print("Executing ML solution . . . ")
            end_to_end_response = end_to_end_response and \
                                  run_router_ml(ext_port, infer_port, project_name, ext_ip, infer_ip)

        if end_to_end_response:
            run_id = get_current_run_id()
            join_output(project_name=project_name,
                        pdf_folder = destination_pdf, 
                        rb_output_folder = destination_rb_infer, 
                        ml_output_folder = destination_ml_infer, 
                        output_folder= destination_output, 
                        use_docker = rb_use_docker, 
                        work_dir_rb = destination_rb_workdir, 
                        verbosity = rb_verbosity, 
                        rb_port=rb_port, 
                        rb_ip=rb_ip,
                        run_id= run_id)
            if(enable_db_export):
                print("Exporting output to database . . . ")
                run_db_export(project_name, project_settings['data_export'], run_id)
            if project_settings['extraction']['store_extractions']:
                print("Finally we transfer the text extraction to the output folder.")
                source_extraction_data = destination_ml_extraction
                destination_extraction_data = project_data_dir + r'/output/TEXT_EXTRACTION'
                os.makedirs(destination_extraction_data, exist_ok=True)
                end_to_end_response = copy_files_without_overwrite(source_extraction_data, destination_extraction_data)
            if project_settings['general']['delete_interim_files']:
                create_directory(destination_ml_extraction)
                create_directory(destination_rb_workdir)
                create_directory(destination_pdf)
                create_directory(destination_mapping)
            if end_to_end_response:
                print("End-to-end inference complete")
    
    except Exception as e:
        print('Process failed to run. Reason:' + str(repr(e)) + traceback.format_exc())

    clear_running()


if __name__ == "__main__":
    main()
