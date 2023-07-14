from pathlib import Path
import config_path
from train_on_pdf import link_files, link_extracted_files
import shutil

def test_link_files(temporary_folder: Path):
    """Tests if link_files creates proper hard links"""
    path_test_directory_source = temporary_folder / 'source'
    path_test_directory_destination = temporary_folder / 'destination'
    path_test_directory_source.mkdir(parents = True)
    path_test_directory_destination.mkdir(parents = True)
    
    # create sample files
    for i in range(10):
        path_current_test_file = path_test_directory_source / f'test_{i}.txt'
        path_current_test_file.touch()
    
    # perform the linking
    link_files(str(path_test_directory_source), str(path_test_directory_destination))
    
    for i in range(10):
        path_current_test_file = path_test_directory_source / f'test_{i}.txt'
        # check for hard links
        assert path_current_test_file.stat().st_nlink == 2

    # cleanup
    shutil.rmtree(temporary_folder)

def test_link_extracted_files(temporary_folder: Path):
    pass