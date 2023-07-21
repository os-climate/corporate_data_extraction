from pathlib import Path
from train_on_pdf import set_running, check_running, clear_running
import pytest
from unittest.mock import patch


@pytest.fixture
def path_file_running(path_folder_temporary: Path):
    """Defines a fixture for the running_file path

    :param path_folder_temporary: _description_
    :type path_folder_temporary: Path
    :yield: Path for the running_file
    :rtype: Path
    """
    path_file_running_ = path_folder_temporary / 'running'
    yield path_file_running_


def test_set_running(path_file_running):
    """Tests the set_running function creating a running file

    :param path_file_running: Requesting the temporary folder fixture
    :type path_file_running: Path
    """
    with patch('train_on_pdf.path_file_running', str(path_file_running)):
        set_running()
        assert path_file_running.exists()


def test_checking_onging_run(path_file_running):
    """Tests the return value of check_running for ongoing runs

    :param path_file_running: Requesting the temporary folder fixture
    :type path_file_running: Path
    """
    with patch('train_on_pdf.path_file_running', str(path_file_running)):
        path_file_running.touch()
        assert check_running() == True


def test_checking_finished_run(path_file_running):
    """Tests the return value of check_running for finished runs

    :param path_file_running: Requesting the temporary folder fixture
    :type path_file_running: Path
    """
    path_file_running.unlink(missing_ok = True)
    with patch('train_on_pdf.path_file_running', str(path_file_running)):
        assert check_running() == False
       

def test_clear_running(path_file_running):
    """Tests for clearing running file

    :param path_file_running: Requesting the temporary folder fixture
    :type path_file_running: Path
    """
    path_file_running.touch()
    with patch('train_on_pdf.path_file_running', str(path_file_running)):
        clear_running()
        assert not path_file_running.exists()

