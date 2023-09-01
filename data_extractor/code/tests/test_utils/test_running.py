from pathlib import Path
from utils.utils import set_running, check_running, clear_running, TrainingMonitor
import pytest
from unittest.mock import patch, Mock
import config_path
from utils.paths import path_file_running


# @pytest.fixture
# def prerequisite_running(path_folder_root_testing: Path):
#     """Defines a fixture for the running_file path

#     :param path_folder_root_testing: Path for the testing folder
#     :type path_folder_root_testing: Path
#     """
#     # path_file_running = path_folder_root_testing / 'data' / 'running'
#     # # mock the path to the running file
#     # with patch('train_on_pdf.path_file_running', 
#     #            str(path_file_running)):
#     yield

#     # cleanup
#     path_file_running.unlink(missing_ok=True)
    
@pytest.fixture
def training_monitor() -> TrainingMonitor:
    """The fixture returns a TrainingMonitor object for testing

    :yield: TrainingMonitor class for monitor training status
    :rtype: TrainingMonitor
    """
    _train_monitor = TrainingMonitor(path_file_running)
    yield _train_monitor
    # clean up
    _train_monitor._delete_path_file_running()
        

def test_set_running(path_folder_root_testing: Path,
                     training_monitor: TrainingMonitor):
    """Tests the set_running function creating a running file

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    # set path to running file and do a cleanup
    # path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.unlink(missing_ok=True)
    
    # perform set_running and assert that running file exists
    training_monitor.set_running()
    assert path_file_running.exists()


def test_checking_onging_run(path_folder_root_testing: Path,
                             training_monitor: TrainingMonitor):
    """Tests the return value of check_running for ongoing runs

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    # path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.touch()
    assert training_monitor.check_running() == True


def test_checking_finished_run(path_folder_root_testing: Path,
                               training_monitor: TrainingMonitor):
    """Tests the return value of check_running for finished runs

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    # path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.unlink(missing_ok = True)
    assert training_monitor.check_running() == False
       

def test_clear_running(path_folder_root_testing: Path,
                       training_monitor: TrainingMonitor):
    """Tests for clearing running file

    :param prerequisite_running: Fixture for prerequisite of running funcions
    :type prerequisite_running: None
    :param path_folder_root_testing: Path for the testing folder
    :type path_folder_root_testing: Path
    """
    # path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.touch()
    training_monitor.clear_running()
    assert not path_file_running.exists()
