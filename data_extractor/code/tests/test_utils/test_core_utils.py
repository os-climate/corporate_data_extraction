from pathlib import Path
from utils.core_utils import create_folder, copy_file_without_overwrite
import shutil
import pytest


@pytest.fixture()
def prerequisites_copy_file_without_overwrite(path_folder_temporary: Path) -> None:
    """Defines a fixture for creating the source and destination folder

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :rtype: None
    """
    path_folder_source = path_folder_temporary / 'source'
    path_folder_destination = path_folder_temporary / 'destination'
    path_folder_source.mkdir(parents = True)
    path_folder_destination.mkdir(parents = True)
    yield
    
    # cleanup
    for path in path_folder_temporary.glob("*"):
        shutil.rmtree(path)


def test_create_folder(path_folder_temporary: Path):
    """Tests of create_folder creates a folder

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    create_folder(str(path_folder_temporary))
    
    assert path_folder_temporary.exists()


def test_create_folder_cleanup(path_folder_temporary: Path):
    """Tests of create_folder performs a clean-up if folder exists

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    path_folder_temporary.mkdir(exist_ok = True)
    for i in range(10):
        path_current_test_file = path_folder_temporary / f'test_{i}.txt'
        path_current_test_file.touch()
        
    create_folder(str(path_folder_temporary))
    assert not any(path_folder_temporary.iterdir())
    
    
def test_copy_file_without_overwrite_result(prerequisites_copy_file_without_overwrite,
                                            path_folder_temporary: Path):
    """Tests if copy_file_without_overwrite returns True if executed
    Requesting prerequisites_copy_file_without_overwrite automatically (autouse)
    
    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    path_folder_source = path_folder_temporary / 'source'
    path_folder_destination = path_folder_temporary / 'destination'
    path_folder_source_file = path_folder_source / 'test.txt'
    path_folder_source_file.touch()
    
    result = copy_file_without_overwrite(str(path_folder_source), str(path_folder_destination))
    assert result == True
    
    
def test_copy_file_without_overwrite_file_not_exists(prerequisites_copy_file_without_overwrite,
                                                     path_folder_temporary: Path):
    """Tests that copy_file_without_overwrite copies the files from the source to the 
    destination folder if they do no exist in the destination folder
    Requesting prerequisites_copy_file_without_overwrite automatically (autouse)
    
    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    path_folder_source = path_folder_temporary / 'source'
    path_folder_destination = path_folder_temporary / 'destination'
    path_folder_source_file = path_folder_source / 'test.txt'
    path_folder_source_file.touch()
    
    path_folder_destination_file = path_folder_destination / 'test.txt'
    assert not path_folder_destination_file.exists()
    
    copy_file_without_overwrite(str(path_folder_source), str(path_folder_destination))
    assert path_folder_destination_file.exists()