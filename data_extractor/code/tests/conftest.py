import os
import shutil
import sys
from pathlib import Path

import config_path
import pandas as pd
import pytest
from tests.utils_test import project_tests_root

# add test_on_pdf.py to the PATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


@pytest.fixture(scope="session")
def path_folder_temporary() -> Path:
    """Fixture for defining path for running check

    :return: Path to the temporary folder
    :rtype: Path
    :yield: Path to the temporary folder
    :rtype: Iterator[Path]
    """
    path_folder_temporary_ = project_tests_root() / "temporary_folder"
    # delete the temporary folder and recreate it
    shutil.rmtree(path_folder_temporary_, ignore_errors=True)
    path_folder_temporary_.mkdir()
    yield path_folder_temporary_

    # cleanup
    shutil.rmtree(path_folder_temporary_, ignore_errors=True)


@pytest.fixture(scope="session")
def path_folder_root_testing() -> Path:
    path_folder_data_sample_ = project_tests_root() / "root_testing"
    yield path_folder_data_sample_
