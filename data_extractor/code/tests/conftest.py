import os
import config_path
import pytest
from pathlib import Path
import shutil
import pandas as pd
import sys
from tests.utils_test import project_root
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# TODO: remove path_file_running fixture


# @pytest.fixture(scope='session')
# def path_file_running() -> Path:
#     """Fixture for defining path for running check"""
#     path_file_running_ = Path(config_path.NLP_DIR + r'/data/running')
#     yield path_file_running_
#     shutil.rmtree(path_file_running_, ignore_errors = True)
    

@pytest.fixture(scope='session')
def path_folder_temporary() -> Path:
    """Fixture for defining path for running check"""
    path_folder_temporary_ = project_root() / 'temporary_folder'
    shutil.rmtree(path_folder_temporary_, ignore_errors = True)
    path_folder_temporary_.mkdir()
    yield path_folder_temporary_
    shutil.rmtree(path_folder_temporary_, ignore_errors = True)

