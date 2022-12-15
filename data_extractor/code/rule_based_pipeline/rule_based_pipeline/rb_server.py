import argparse
import os

from flask import Flask, Response, request

app = Flask(__name__)

def run_rb_int(raw_pdf_folder, working_folder, output_folder, verbosity):
        cmd = 'python3 /app/code/rule_based_pipeline/rule_based_pipeline/main.py' + \
              ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
              ' --working_folder "' + working_folder + '"' +    \
              ' --output_folder "' + output_folder + '"'  +     \
              ' --verbosity ' + str(verbosity)
        print("Running command: " + cmd)
        os.system(cmd)

def run_rb(project_name, verbosity):
    base = r'/app/data/' + project_name 
    raw_pdf_folder = base + r'/interim/pdfs/'
    working_folder = base + r'/interim/rb/work'
    output_folder = base + r'/output/KPI_EXTRACTION/rb'
    run_rb_int(raw_pdf_folder, working_folder, output_folder, verbosity)

@app.route("/liveness")
def liveness():
    return Response(response={}, status=200)


@app.route("/run")
def run():
    project_name = request.args['project_name']
    verbosity  = int(request.args['verbosity'])
    run_rb(project_name, verbosity)
    return Response(response={}, status=200)


@app.route("/run_xy_ml")
def run_xy_ml():
    project_name = request.args['project_name']
    base = r'/app/data/' + project_name 
    raw_pdf_folder = base + r'/interim/pdfs/'
    working_folder = base + r'/interim/rb/work'
    output_folder = base + r'/output/KPI_EXTRACTION'
    csv_path = output_folder + '/' + request.args['csv_name']
    cmd = 'python3 /app/code/rule_based_pipeline/rule_based_pipeline/main_find_xy.py' + \
             ' --raw_pdf_folder "' + raw_pdf_folder + '"' +    \
             ' --working_folder "' + working_folder + '"' +    \
             ' --pdf_name "' + request.args['pdf_name'] + '"'  +     \
             ' --csv_name "' + csv_path + '"'  +     \
             ' --output_folder "' + output_folder + '"'  +     \
             ' --verbosity ' + str(request.args['verbosity'])
    print("Running command: " + cmd)
    os.system(cmd)
    
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
