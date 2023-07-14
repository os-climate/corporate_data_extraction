import os
import config_path
import pytest
from pathlib import Path
import shutil

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

@pytest.fixture(scope='session')
def file_running() -> Path:
    """Define path for running check"""
    path_file_running = Path(config_path.NLP_DIR + r'/data/running')
    yield path_file_running
    shutil.rmtree(path_file_running, ignore_errors = True)
    

@pytest.fixture(scope='session')
def temporary_folder() -> Path:
    """Define path for running check"""
    path_temporary_folder = Path(config_path.NLP_DIR + r'/temporary_folder')
    yield path_temporary_folder
    shutil.rmtree(path_temporary_folder, ignore_errors = True)