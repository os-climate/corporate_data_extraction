from pathlib import Path
import config_path
from train_on_pdf import generate_text_3434
from tests.utils_test import write_to_file
import shutil
from unittest.mock import patch


def test_generate_text(path_folder_temporary: Path):
    """Tests the generate_text_3434 which takes files from the folder relevance,
    reads them in and puts the content into the file text_3434.csv. Note that
    the header of text_3434.csv is taken from the first file read in"""
    project_name = 'test'
    path_folder_relevance = path_folder_temporary / 'relevance'
    path_folder_text_3434 = path_folder_temporary / 'folder_test_3434'
    path_folder_relevance.mkdir(parents = True)
    path_folder_text_3434.mkdir(parents = True)
    
    # create multiple files in the folder_relevance with the same header
    for i in range(5):
        path_current_file = path_folder_relevance / f'test_{i}.csv'
        path_current_file.touch()
        write_to_file(path_current_file, f'That is a test {i}', 'HEADER')
    
    # mock the global variables required for generate_text_3434 and execute the function
    with (patch('train_on_pdf.folder_relevance', str(path_folder_relevance)),
          patch('train_on_pdf.folder_text_3434', str(path_folder_text_3434))):
        generate_text_3434(project_name)
    
    # ensure that the header and the content form the first file is written to 
    # the file text_3434.csv in folder relevance and the the content of the other
    # files in folder relevance is appended without the header

    # check if file_3434 exists
    path_file_text_3434_csv = path_folder_text_3434 / 'text_3434.csv'
    assert path_file_text_3434_csv.exists()
    
    # check if header and content of files exist
    with open(str(path_file_text_3434_csv), 'r') as file_text_3434:
        for line_number, line_content in enumerate(file_text_3434, start = -1):
            if line_number == -1:
                assert line_content.rstrip() == 'HEADER'
            else:
                assert line_content.rstrip() == f'That is a test {line_number}'
                
    # cleanup
    shutil.rmtree(path_folder_temporary)