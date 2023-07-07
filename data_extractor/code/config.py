import os
from pathlib import Path
from pydantic import BaseSettings

os.chdir(Path(__file__).parent)


class Config(BaseSettings):
    """
    Default Config Class
    """
    try:
        PATH = globals()['_dh'][0]
    except KeyError:
        PATH = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = os.path.dirname(PATH)

    MODEL_DIR = ROOT_DIR + r'/models'
    DATA_DIR = ROOT_DIR + r'/data'
    NLP_DIR = ROOT_DIR
    FILE_RUNNING = NLP_DIR + r'/data/running'
    #DATA_OUTPUT_DIR = r'/app/ids/NLP/data_output'

    PYTHON_EXECUTABLE = 'python'


global config
config = Config()


def get_config() -> Config:
    """
    Return the default Config object
    """
    return config
