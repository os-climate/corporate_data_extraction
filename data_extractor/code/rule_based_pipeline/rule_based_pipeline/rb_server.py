import argparse
import os
import json
from s3_communication import S3Communication
import traceback

from flask import Flask, Response, request

app = Flask(__name__)


def create_directory(directory_name):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def run_rb_int(raw_pdf_folder, working_folder, output_folder, verbosity):
    cmd = 'python3 /app/code/rule_based_pipeline/rule_based_pipeline/main.py' + \
          ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
          ' --working_folder "' + working_folder + '"' +    \
          ' --output_folder "' + output_folder + '"'  +     \
          ' --verbosity ' + str(verbosity)
    print("Running command: " + cmd)
    os.system(cmd)


def run_rb(project_name, verbosity, s3_usage, s3_settings):
    base = r'/app/data/' + project_name 
    raw_pdf_folder = base + r'/interim/pdfs/'
    working_folder = base + r'/interim/rb/work'
    output_folder = base + r'/output/KPI_EXTRACTION/rb'
    if s3_usage:
        s3c_main = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
            aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
            aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
            s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
        )
        create_directory(base)
        create_directory(raw_pdf_folder)
        create_directory(working_folder)
        create_directory(output_folder)
        project_prefix = s3_settings['prefix'] + "/" + project_name + '/data'
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/pdfs/inference', 
                                    raw_pdf_folder)
    run_rb_int(raw_pdf_folder, working_folder, output_folder, verbosity)
    if s3_usage:
        s3c_main.upload_files_in_dir_to_prefix(output_folder, 
                                  project_prefix + '/output/KPI_EXTRACTION/rb')
    return True


@app.route("/liveness")
def liveness():
    return Response(response={}, status=200)


@app.route("/run")
def run():
    try:
        args = json.loads(request.args['payload'])
        project_name = args['project_name']
        s3_settings = None
        if args['s3_usage']:
            s3_settings = args["s3_settings"]
        verbosity  = int(args['verbosity'])
        run_rb(project_name, verbosity, args['s3_usage'], s3_settings)
        return Response(response={}, status=200)
    except Exception as e:
        m = traceback.format_exc()
        return Response(response={m}, status=200)


@app.route("/run_xy_ml")
def run_xy_ml():
    args = json.loads(request.args['payload'])
    project_name = args['project_name']
    base = r'/app/data/' + project_name 
    raw_pdf_folder = base + r'/interim/pdfs/'
    working_folder = base + r'/interim/rb/work'
    output_folder = base + r'/output/KPI_EXTRACTION/joined_ml_rb'
    csv_path = output_folder + '/' + args['csv_name']
    if args['s3_usage']:
        s3_settings = args["s3_settings"]
        s3c_main = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings['main_bucket']['s3_endpoint']),
            aws_access_key_id=os.getenv(s3_settings['main_bucket']['s3_access_key']),
            aws_secret_access_key=os.getenv(s3_settings['main_bucket']['s3_secret_key']),
            s3_bucket=os.getenv(s3_settings['main_bucket']['s3_bucket_name']),
        )
        create_directory(base)
        create_directory(raw_pdf_folder)
        create_directory(working_folder)
        create_directory(output_folder)
        project_prefix = s3_settings['prefix'] + "/" + project_name + '/data'
        s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/pdfs/inference', 
                            raw_pdf_folder)
        s3c_main.download_file_from_s3(csv_path, project_prefix + '/output/KPI_EXTRACTION/joined_ml_rb', args['csv_name'])
    cmd = 'python3 /app/code/rule_based_pipeline/rule_based_pipeline/main_find_xy.py' + \
             ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
             ' --working_folder "' + working_folder + '"' +    \
             ' --pdf_name "' + args['pdf_name'] + '"'  +     \
             ' --csv_name "' + csv_path + '"'  +     \
             ' --output_folder "' + output_folder + '"'  +     \
             ' --verbosity ' + str(args['verbosity'])
    print("Running command: " + cmd)
    os.system(cmd)
    if args['s3_usage']:
        s3c_main.upload_file_to_s3(filepath=csv_path,
                      s3_prefix=project_prefix + '/output/KPI_EXTRACTION/joined_ml_rb',
                      s3_key=args['csv_name'])
    return Response(response={}, status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='rb server')
    # Add the arguments
    parser.add_argument('--port',
                        type=int,
                        default=8000,
                        help='port to use for the infer server')
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)
