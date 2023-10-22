import argparse
import json
import os
import traceback

from flask import Flask, Response, request
from config_path import NLP_DIR

app = Flask(__name__)


def check_running():
    print(NLP_DIR+r'/data/running')
    return os.path.exists(NLP_DIR+r'/data/running')


@app.route("/liveness")
def liveness():
    return Response(response={}, status=200)


@app.route("/running")
def running():
    return Response(response={str(check_running())}, status=200)


@app.route("/train")
def train():
    """ This function should start the train_on_pdf.py with given parameters as a web access point.

    :return:
    """
    parser_train = argparse.ArgumentParser(description='End-to-end training')

    parser_train.add_argument('--project_name',
                              type=str,
                              default=None,
                              help='Name of the Project')

    parser_train.add_argument('--s3_usage',
                              type=str,
                              default=None,
                              help='Do you want to use S3? Type either Y or N.')

    # Read arguments from direct python call
    args_train = parser_train.parse_args()
    try:
        project_name = args_train.project_name
        s3_usage = args_train.s3_usage
    except AttributeError:
        pass

    # Read arguments from wget call
    if project_name is None or s3_usage is None:
        try:
            project_name = request.args.get("project_name")
            s3_usage = request.args.get("s3_usage")
        except AttributeError:
            pass

    # Read arguments from payload if given
    if project_name is None or s3_usage is None:
        try:
            args_train = json.loads(request.args['payload'])
            project_name = args_train["project_name"]
            s3_usage = args_train["s3_usage"]
        except Exception:
            msg = "Project name or s3_usage where not given via command or payload. Please recheck your call."
            return Response(msg, status=500)

    cmd = 'python3 train_on_pdf.py' + \
          ' --project_name "' + project_name + '"' + \
          ' --s3_usage "' + s3_usage + '"'
    print("Running command: " + cmd)
    try:
        os.system(cmd)
    except Exception as e:
        msg = "Error during train_on_pdf.py \nException:" + str(repr(e) + traceback.format_exc())
        return Response(msg, status=500)
    msg = "train_on_pdf.py was executed without any error. Check the results please."
    return Response(msg, status=200)


@app.route("/infer")
def infer():
    """ This function should start the infer_on_pdf.py with given parameters (either via cli arguments or via
     payload) as a web access point.

    :return: Response type containing a message and the int for the type of message (200 if ok, 500 if error)
    """
    parser_infer = argparse.ArgumentParser(description='End-to-end inference')

    parser_infer.add_argument('--project_name',
                              type=str,
                              default=None,
                              help='Name of the Project')

    parser_infer.add_argument('--s3_usage',
                              type=str,
                              default=None,
                              help='Do you want to use S3? Type either Y or N.')

    parser_infer.add_argument('--mode',
                              type=str,
                              default='both',
                              help='Inference Mode (RB, ML, both, or none - for just doing postprocessing)')

    args_infer = parser_infer.parse_args()
    project_name = args_infer.project_name
    s3_usage = args_infer.s3_usage
    mode = args_infer.mode

    # Read arguments from wget call
    if project_name is None or s3_usage is None:
        try:
            project_name = request.args.get("project_name")
            s3_usage = request.args.get("s3_usage")
            mode = request.args.get("mode")
        except AttributeError:
            pass

    # Read arguments from payload if given
    if project_name is None or s3_usage is None:
        try:
            args_infer = json.loads(request.args['payload'])
            project_name = args_infer["project_name"]
            s3_usage = args_infer["s3_usage"]
            mode = args_infer["mode"]
        except Exception:
            msg = "Project name, mode or s3_usage where not given via command or payload. Please recheck your call."
            return Response(msg, status=500)

    cmd = 'python3 infer_on_pdf.py' + \
          ' --project_name "' + project_name + '"' + \
          ' --mode "' + mode + '"' + \
          ' --s3_usage "' + s3_usage + '"'
    print("Running command: " + cmd)
    try:
        os.system(cmd)
    except Exception as e:
        msg = "Error during infer_on_pdf.py \nException:" + str(repr(e) + traceback.format_exc())
        return Response(msg, status=500)
    msg = "infer_on_pdf.py was executed without any error. Check the results please."
    return Response(msg, status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coordinator server')
    parser.add_argument('--port',
                        type=int,
                        default=2000,
                        help='Port to use for the coordinator server')
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)
