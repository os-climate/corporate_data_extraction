from pathlib import Path
from utils.core_utils import create_folder, copy_file_without_overwrite, _delete_file, _delete_files_in_folder
import shutil
import pytest
from unittest.mock import patch, Mock


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
    
    
def test_create_folder_already_exists():
    path_folder_as_str = 'test'
    with (patch.object(Path, 'mkdir') as mocked_path,
          patch('utils.core_utils._delete_files_in_folder') as mocked_mkdir):
        mocked_path.side_effect = OSError
        
        create_folder(path_folder_as_str)
        mocked_mkdir.assert_called_once()
        
        
def test_create_folder_path_not_exists():
    path_folder_as_str = 'test'
    with (patch.object(Path, 'mkdir') as mocked_path,
          patch('utils.core_utils._delete_files_in_folder') as mocked_mkdir):
        mocked_path.side_effect = FileNotFoundError
        
        create_folder(path_folder_as_str)
        mocked_mkdir.assert_called_once()
    
    
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
    
    
def test_delete_file(path_folder_temporary: Path):
    path_file_temporary = path_folder_temporary / 'test.txt'
    path_file_temporary.touch()
    
    _delete_file(path_file_temporary)
    assert not path_file_temporary.exists()
    

def test_delete_files_in_folder(path_folder_temporary: Path):
    for i in range(5):
        path_file_current = path_folder_temporary / f'test_{i}.txt'
        path_file_current.touch()
        
    _delete_files_in_folder(path_folder_temporary)
    assert not any(path_folder_temporary.iterdir())