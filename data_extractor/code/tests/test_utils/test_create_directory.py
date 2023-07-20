from pathlib import Path
import config_path
from train_on_pdf import create_directory
import shutil


def test_create_directory(path_temporary_folder: Path):
    """Tests of create_directory creates a folder

    :param path_temporary_folder: Requesting the temporary folder fixture
    :type path_temporary_folder: Path
    """
    # call create_folder and check if the folder exists
    create_directory(str(path_temporary_folder))
    assert path_temporary_folder.exists()
    
    # cleanup
    shutil.rmtree(path_temporary_folder)

def test_create_directory_cleanup(path_temporary_folder: Path):
    """Tests of create_directory performs a clean-up if folder exists

    :param path_temporary_folder: Requesting the temporary folder fixture
    :type path_temporary_folder: Path
    """
    # create folder with files
    path_temporary_folder.mkdir(exist_ok = True)
    for i in range(10):
        path_current_test_file = path_temporary_folder / f'test_{i}.txt'
        path_current_test_file.touch()
        
    # call create_directory and check for empty folder
    create_directory(str(path_temporary_folder))
    assert not any(path_temporary_folder.iterdir())
    
    # cleanup
    shutil.rmtree(path_temporary_folder)