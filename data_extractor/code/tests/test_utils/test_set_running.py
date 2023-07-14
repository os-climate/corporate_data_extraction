from pathlib import Path
from train_on_pdf import set_running
import config_path

def test_set_running(file_running: Path):
    """test set_running function"""
    file_running.unlink(missing_ok = True)
    set_running()
    assert Path.exists(file_running)
    # cleanup
    file_running.unlink()
