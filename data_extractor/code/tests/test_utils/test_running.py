from pathlib import Path
from train_on_pdf import set_running, check_running, clear_running
import pytest
from unittest.mock import patch, Mock
import config_path


@pytest.fixture
def prerequisite_running(path_folder_root_testing: Path):
    """Defines a fixture for the running_file path

    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    # mock the path to the running file
    with patch('train_on_pdf.path_file_running', 
               str(path_file_running)):
        yield

        # cleanup
        path_file_running.unlink(missing_ok=True)
        

def test_set_running(prerequisite_running, path_folder_root_testing: Path):
    """Tests the set_running function creating a running file

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    # set path to running file and do a cleanup
    path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.unlink(missing_ok=True)
    
    # perform set_running and assert that running file exists
    set_running()
    assert path_file_running.exists()
    
    # cleanup
    path_file_running.unlink()


def test_checking_onging_run(prerequisite_running, path_folder_root_testing: Path):
    """Tests the return value of check_running for ongoing runs

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.touch()
    assert check_running() == True


def test_checking_finished_run(prerequisite_running, path_folder_root_testing: Path):
    """Tests the return value of check_running for finished runs

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.unlink(missing_ok = True)
    assert check_running() == False
       

def test_clear_running(prerequisite_running, path_folder_root_testing: Path):
    """Tests for clearing running file

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.touch()
    clear_running()
    assert not path_file_running.exists()