from pathlib import Path
import config_path
from train_on_pdf import create_directory
import shutil


def test_create_directory(temporary_folder: Path):
    """Tests of create_directory creates a directory"""
    create_directory(str(temporary_folder))
    assert temporary_folder.exists()
    # cleanup
    shutil.rmtree(temporary_folder)

def test_create_directory_cleanup(temporary_folder: Path):
    """Tests of create_directory performs a clean-up if directory exists"""
    # create folder with files
    temporary_folder.mkdir(exist_ok = True)
    for i in range(10):
        path_current_test_file = temporary_folder / f'test_{i}.txt'
        path_current_test_file.touch()
    # call create_directory and check for empty folder
    create_directory(str(temporary_folder))
    assert not any(temporary_folder.iterdir())
    # cleanup
    shutil.rmtree(temporary_folder)