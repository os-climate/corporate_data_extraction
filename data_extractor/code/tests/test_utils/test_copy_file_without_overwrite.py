from pathlib import Path
import config_path
from train_on_pdf import copy_file_without_overwrite
import shutil
import pytest

    
@pytest.fixture
def path_required_folders(path_temporary_folder: Path) -> tuple[Path, Path]:
    """Defines a fixture for creating the source and destination folder

    :param path_temporary_folder: Requesting the temporary folder fixture
    :type path_temporary_folder: Path
    :return: Tuple containing the paths to the source and destination folders
    :rtype: tuple[Path, Path]
    :yield: Tuple containing the paths to the source and destination folders
    :rtype: Iterator[tuple[Path, Path]]
    """
    path_folder_source = path_temporary_folder / 'source'
    path_folder_destination = path_temporary_folder / 'destination'
    path_folder_source.mkdir(parents = True)
    path_folder_destination.mkdir(parents = True)
    yield (path_folder_source, path_folder_destination)
    
    # cleanup 
    shutil.rmtree(path_temporary_folder)


def test_copy_file_without_overwrite_result(path_required_folders: tuple[Path, Path]):
    """Tests if copy_file_without_overwrite returns True if executed

    :param path_required_folders: Tuple containing the paths to the source and destination folders
    :type path_required_folders: tuple[Path, Path]
    """

    # create test file in source folder
    path_folder_source, path_folder_destination = path_required_folders
    path_folder_source_file = path_folder_source / 'test.txt'
    path_folder_source_file.touch()
    
    # execute copy_file_without_overwrite
    result = copy_file_without_overwrite(str(path_folder_source), str(path_folder_destination))
    assert result == True
    
    
def test_copy_file_without_overwrite_file_not_exists(path_required_folders: tuple[Path, Path]):
    """Tests that copy_file_without_overwrite copies the files from the source to the 
    destination folder if they do no exist in the destination folder

    :param path_required_folders: Tuple containing the paths to the source and destination folders
    :type path_required_folders: tuple[Path, Path]
    """
    # create test file in source folder
    path_folder_source, path_folder_destination = path_required_folders
    path_folder_source_file = path_folder_source / 'test.txt'
    path_folder_source_file.touch()
    
    # create test file path for destination folder
    path_folder_destination_file = path_folder_destination / 'test.txt'
    assert not path_folder_destination_file.exists()
    
    # execute copy_file_without_overwrite
    copy_file_without_overwrite(str(path_folder_source), str(path_folder_destination))
    assert path_folder_destination_file.exists()
