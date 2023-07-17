from pathlib import Path
import config_path
from train_on_pdf import copy_file_without_overwrite
import shutil


def test_copy_file_without_overwrite_result(path_temporary_folder: Path):
    """Tests if copy_file_without_overwrite returns True if executed"""
    # create source and destination folder
    path_folder_source = path_temporary_folder / 'source'
    path_folder_destination = path_temporary_folder / 'destination'
    path_folder_source.mkdir(parents = True)
    path_folder_destination.mkdir(parents = True)
    
    # create test file in source folder
    path_folder_source_file = path_folder_source / 'test.txt'
    path_folder_source_file.touch()
    
    # execute copy_file_without_overwrite
    result = copy_file_without_overwrite(str(path_folder_source), str(path_folder_destination))
    assert result == True
    
    # cleanup
    shutil.rmtree(path_temporary_folder)
    
    
def test_copy_file_without_overwrite(path_temporary_folder: Path):
    # create source and destination folder
    path_folder_source = path_temporary_folder / 'source'
    path_folder_destination = path_temporary_folder / 'destination'
    path_folder_source.mkdir(parents = True)
    path_folder_destination.mkdir(parents = True)
    
    # create test file in source folder
    path_folder_source_file = path_folder_source / 'test.txt'
    path_folder_source_file.touch()
    
    # create test file path for destination folder
    path_folder_destination_file = path_folder_destination / 'test.txt'
    assert not path_folder_destination_file.exists()
    
    # execute copy_file_without_overwrite
    copy_file_without_overwrite(str(path_folder_source), str(path_folder_destination))
    assert path_folder_destination_file.exists()
    
    # cleanup
    shutil.rmtree(path_temporary_folder)