import os
import pytest
from pathlib import Path
import shutil
import pandas as pd
import sys
from tests.utils_test import project_tests_root
from utils.settings import get_s3_settings, get_main_settings, S3Settings, MainSettings, Settings
from utils.paths import ProjectPaths, get_project_settings
# add test_on_pdf.py to the PATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
  

@pytest.fixture(scope='session')
def path_folder_temporary() -> Path:
    """Fixture for defining path for running check

    :return: Path to the temporary folder
    :rtype: Path
    :yield: Path to the temporary folder
    :rtype: Iterator[Path]
    """
    path_folder_temporary_ = project_tests_root() / 'temporary_folder'
    # delete the temporary folder and recreate it
    shutil.rmtree(path_folder_temporary_, ignore_errors = True)
    path_folder_temporary_.mkdir()
    yield path_folder_temporary_
    
    # cleanup
    shutil.rmtree(path_folder_temporary_, ignore_errors = True)
    
    
@pytest.fixture(scope='session')
def path_folder_root_testing() -> Path:
    path_folder_data_sample_ = project_tests_root() / 'root_testing'
    yield path_folder_data_sample_


@pytest.fixture(scope='session')
def main_settings() -> MainSettings:
    return get_main_settings()


@pytest.fixture(scope='session')
def s3_settings() -> S3Settings:
    return get_s3_settings()


@pytest.fixture(scope='session')
def project_paths(main_settings: Settings) -> ProjectPaths:
    return ProjectPaths('test_project', main_settings)

