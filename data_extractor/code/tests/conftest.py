import os
import config_path
import pytest
from pathlib import Path
import shutil

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

@pytest.fixture(scope='session')
def path_file_running() -> Path:
    """Define path for running check"""
    path_file_running_ = Path(config_path.NLP_DIR + r'/data/running')
    yield path_file_running_
    shutil.rmtree(path_file_running_, ignore_errors = True)
    

@pytest.fixture(scope='session')
def path_temporary_folder() -> Path:
    """Define path for running check"""
    path_temporary_folder_ = Path(config_path.NLP_DIR + r'/path_temporary_folder')
    yield path_temporary_folder_
    shutil.rmtree(path_temporary_folder_, ignore_errors = True)