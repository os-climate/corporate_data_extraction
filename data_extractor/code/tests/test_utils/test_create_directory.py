from pathlib import Path
from train_on_pdf import create_directory
import shutil


def test_create_directory(path_folder_temporary: Path):
    """Tests of create_directory creates a folder

    :param path_folder_temporary: Requesting the temporary folder fixture
    :type path_folder_temporary: Path
    """
    # call create_folder and check if the folder exists
    create_directory(str(path_folder_temporary))
    assert path_folder_temporary.exists()


def test_create_directory_cleanup(path_folder_temporary: Path):
    """Tests of create_directory performs a clean-up if folder exists

    :param path_folder_temporary: Requesting the temporary folder fixture
    :type path_folder_temporary: Path
    """
    # create folder with files
    path_folder_temporary.mkdir(exist_ok = True)
    for i in range(10):
        path_current_test_file = path_folder_temporary / f'test_{i}.txt'
        path_current_test_file.touch()
        
    # call create_directory and check for empty folder
    create_directory(str(path_folder_temporary))
    assert not any(path_folder_temporary.iterdir())