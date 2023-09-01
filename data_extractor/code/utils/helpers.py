import tempfile
from pathlib import Path
import os

def create_tmp_file_path() -> Path:
    # _, path_tmp_file = tempfile.mkstemp()
    # os.remove(path_tmp_file)
    # return Path(path_tmp_file)
    return Path(__file__).parent.resolve() / 'running'