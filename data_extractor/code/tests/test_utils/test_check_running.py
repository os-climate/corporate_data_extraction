from pathlib import Path
from train_on_pdf import check_running
import config_path


def test_checking_onging_run(path_file_running: Path):
    """Tests the return value of check_running for ongoing runs"""
    path_file_running.touch()
    assert check_running() is True
    # cleanup
    path_file_running.unlink()


def test_checking_finished_run(path_file_running: Path):
    """Tests the return value of check_running for finished runs"""
    path_file_running.unlink(missing_ok = True)
    assert check_running() is False
