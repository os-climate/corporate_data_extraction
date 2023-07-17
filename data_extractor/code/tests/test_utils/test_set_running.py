from pathlib import Path
from train_on_pdf import set_running
import config_path

def test_set_running(path_file_running: Path):
    """test set_running function"""
    path_file_running.unlink(missing_ok = True)
    set_running()
    assert Path.exists(path_file_running)
    # cleanup
    path_file_running.unlink()
