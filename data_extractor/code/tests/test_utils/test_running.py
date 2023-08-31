from pathlib import Path
from train_on_pdf import set_running, check_running, clear_running
import pytest
from unittest.mock import patch, Mock
import config_path


@pytest.fixture(autouse=True)
def prerequisite_running(path_folder_root_testing: Path):
    """Defines a fixture for the running_file path

<<<<<<< HEAD
<<<<<<< HEAD
    :param path_folder_root_testing: Path for the testing folder
=======
    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
>>>>>>> bd5098e40 (Some cleanup and finishing tests)
    :type path_folder_root_testing: Path
=======
    :param path_folder_data_sample: _description_
    :type path_folder_data_sample: Path
    :yield: Path for the running_file
    :rtype: Path
>>>>>>> ced44e3df (Feature/2023.04 os test (#14))
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    
    with patch('train_on_pdf.path_file_running', str(path_file_running)):
        yield

        # cleanup
        path_file_running.unlink(missing_ok=True)
<<<<<<< HEAD
        
=======
    
    # config_path.root_dir = Mock(side_effect=lambda *args: str(path_file_running))
    # with patch('train_on_pdf.config_path.root_dir'):
        
    #     yield
>>>>>>> ced44e3df (Feature/2023.04 os test (#14))

def test_set_running(path_folder_root_testing: Path):
    """Tests the set_running function creating a running file

    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.unlink(missing_ok=True)
    
    set_running()
    
    assert path_file_running.exists()


def test_checking_onging_run(path_folder_root_testing: Path):
    """Tests the return value of check_running for ongoing runs
    
    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    
    path_file_running.touch()
    
    assert check_running() == True


def test_checking_finished_run(path_folder_root_testing: Path):
    """Tests the return value of check_running for finished runs

    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    
    path_file_running.unlink(missing_ok = True)
    
    assert check_running() == False
       

def test_clear_running(path_folder_root_testing: Path):
    """Tests for clearing running file

    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
    :type path_folder_root_testing: Path
    """
    path_file_running = path_folder_root_testing / 'data' / 'running'
    path_file_running.touch()
    
    clear_running()
    
    assert not path_file_running.exists()

