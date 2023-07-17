from pathlib import Path
from train_on_pdf import clear_running
import config_path


def test_clear_running(path_file_running: Path):
    """test for clearing running file"""
    Path(path_file_running).touch()
    clear_running()
    assert not Path.exists(path_file_running)
