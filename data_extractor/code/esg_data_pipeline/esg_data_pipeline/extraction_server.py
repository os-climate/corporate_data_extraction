import json
import argparse
import glob
import os
import time
from datetime import timedelta
import logging
from flask import Flask, Response, request
import shutil
import traceback

from esg_data_pipeline.components import Extractor
from esg_data_pipeline.config import config
from esg_data_pipeline.components import Curator

app = Flask(__name__)

def create_directory(directory_name):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

@app.route("/liveness")
def liveness():
    return Response(response={}, status=200)


@app.route('/extract/')
def run_extraction():
    args = json.loads(request.args['payload'])
    project_name = args["project_name"]
    extraction_settings = args['extraction']

    BASE_DATA_PROJECT_FOLDER =  config.DATA_FOLDER / project_name    
    config.PDF_FOLDER = BASE_DATA_PROJECT_FOLDER / 'interim' / 'pdfs'    
    BASE_INTERIM_FOLDER = BASE_DATA_PROJECT_FOLDER / 'interim' / 'ml'
    config.EXTRACTION_FOLDER = BASE_INTERIM_FOLDER / 'extraction'
    config.ANNOTATION_FOLDER = BASE_INTERIM_FOLDER / 'annotations'
    config.STAGE = 'extract'
    pdfs = glob.glob(os.path.join(config.PDF_FOLDER, "*.pdf"))
    if len(pdfs) == 0:
        msg = "No pdf files found in the pdf directory ({})".format(config.PDF_FOLDER)
        return Response(msg, status=500)

    config.SEED = extraction_settings["seed"]
    config.PDFTextExtractor_kwargs['min_paragraph_length'] = extraction_settings["min_paragraph_length"]
    config.PDFTextExtractor_kwargs['annotation_folder'] = extraction_settings["annotation_folder"]
    config.PDFTextExtractor_kwargs['skip_extracted_files'] = extraction_settings["skip_extracted_files"]

    ext = Extractor(config.EXTRACTORS)

    try:
        t1 = time.time()
        ext.run_folder(config.PDF_FOLDER, config.EXTRACTION_FOLDER)
        t2 = time.time()
    except Exception as e:
        msg = "Error during extraction\nException:" + str(e)
        return Response(msg, status=500)

    extracted_files = os.listdir(config.EXTRACTION_FOLDER)
    if len(extracted_files) == 0:
        msg = "Extraction Failed. No file was found in the extraction directory ({})"\
            .format(config.EXTRACTION_FOLDER)
        return Response(msg, status=500)

    failed_to_extract = ""
    for pdf in pdfs:
        pdf = os.path.basename(pdf)
        pdf = pdf.split(".pdf")[0]
        if not any([pdf in e for e in extracted_files]):
            failed_to_extract += pdf + "\n"

    msg = "Extraction finished successfully."
    if len(failed_to_extract) > 0:
        msg += "The following pdf files, however,  did not get extracted:\n" + failed_to_extract
    time_elapsed = str(timedelta(seconds=t2 - t1))
    msg += "\nTime elapsed:{}".format(time_elapsed)
    return Response(msg, status=200)


@app.route('/curate/')
def run_curation():
    args = json.loads(request.args['payload'])
    project_name = args["project_name"]
    curation_settings = args["curation"]

    BASE_DATA_PROJECT_FOLDER =  config.DATA_FOLDER / project_name    
    config.PDF_FOLDER = BASE_DATA_PROJECT_FOLDER / 'interim' / 'pdfs'    
    BASE_INTERIM_FOLDER = BASE_DATA_PROJECT_FOLDER / 'interim' / 'ml'
    config.EXTRACTION_FOLDER = BASE_INTERIM_FOLDER / 'extraction'
    config.CURATION_FOLDER = BASE_INTERIM_FOLDER / 'curation'
    config.ANNOTATION_FOLDER = BASE_INTERIM_FOLDER / 'annotations'
    config.KPI_FOLDER = BASE_DATA_PROJECT_FOLDER / 'interim' / 'kpi_mapping'
        
    shutil.copyfile(os.path.join(config.KPI_FOLDER, "kpi_mapping.csv"), "/kpi_mapping.csv")

    config.STAGE = 'curate'
    config.TextCurator_kwargs['retrieve_paragraph'] = curation_settings['retrieve_paragraph']
    config.TextCurator_kwargs['neg_pos_ratio'] = curation_settings['neg_pos_ratio']
    config.TextCurator_kwargs['columns_to_read'] = curation_settings['columns_to_read']
    config.TextCurator_kwargs['company_to_exclude'] = curation_settings['company_to_exclude']
    config.TextCurator_kwargs['min_length_neg_sample'] = curation_settings['min_length_neg_sample']
    config.SEED = curation_settings['seed']

    try:
        if len(config.CURATORS) != 0:
            cur = Curator(config.CURATORS)
            cur.run(config.EXTRACTION_FOLDER, config.ANNOTATION_FOLDER, config.CURATION_FOLDER)
    except Exception as e:
        msg = "Error during curation\nException:" + str(repr(e)) + traceback.format_exc()
        return Response(msg, status=500)
        
    return Response("Curation OK", status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='inference server')
    # Add the arguments
    parser.add_argument('--port',
                        type=int,
                        default=4000,
                        help='port to use for the extract server')
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)
