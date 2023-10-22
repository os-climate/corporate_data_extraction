import os

try:
    path = globals()['_dh'][0]
except KeyError:
    path = os.path.dirname(os.path.realpath(__file__))
    
root_dir = os.path.dirname(path)

MODEL_DIR = root_dir + r'/models'
DATA_DIR = root_dir + r'/data'
NLP_DIR = root_dir

PYTHON_EXECUTABLE = 'python'
