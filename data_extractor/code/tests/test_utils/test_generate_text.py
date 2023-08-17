from pathlib import Path
from train_on_pdf import generate_text_3434
from tests.utils_test import write_to_file
import shutil
from unittest.mock import patch
import pytest


@pytest.fixture
def prerequisites_generate_text(path_folder_temporary: Path) -> Path:
    """Defines a fixture for mocking all required paths and creating required temporary folders

    :param path_folder_temporary: Requesting the temporary folder fixture
    :type path_folder_temporary: Path
    :return: Returning Path object to the temporary sub-folder
    :rtype: Path
    :yield: Returning Path object to the temporary sub-folder
    :rtype: Iterator[Path]
    """
    path_folder_relevance = path_folder_temporary / 'relevance'
    path_folder_text_3434 = path_folder_temporary / 'folder_test_3434'
    path_folder_relevance.mkdir(parents = True)
    path_folder_text_3434.mkdir(parents = True)
    
    # create multiple files in the folder_relevance with the same header
    for i in range(5):
        path_current_file = path_folder_relevance / f'{i}_test.csv'
        path_current_file.touch()
        write_to_file(path_current_file, f'That is a test {i}', 'HEADER')
        
    with (patch('train_on_pdf.folder_relevance', str(path_folder_relevance)),
          patch('train_on_pdf.folder_text_3434', str(path_folder_text_3434))):
        yield path_folder_text_3434
        
        # cleanup
        for path in path_folder_temporary.glob("*"):
            shutil.rmtree(path)


def test_generate_text(prerequisites_generate_text: Path):
    """Tests the generate_text_3434 which takes files from the folder relevance,
    reads them in and puts the content into the file text_3434.csv. Note that
    the header of text_3434.csv is taken from the first file read in

    :param path_folder_temporary: Requesting the prerequistite fixture
    :type path_folder_temporary: Path
    """
    # get the path to the temporary folder
    path_folder_text_3434 = prerequisites_generate_text
    project_name = 'test'
    
    # run the function to test
    generate_text_3434(project_name)
    
    # ensure that the header and the content form the first file is written to 
    # the file text_3434.csv in folder relevance and the the content of the other
    # files in folder relevance is appended without the header

    # check if file_3434 exists
    path_file_text_3434_csv = path_folder_text_3434 / 'text_3434.csv'
    assert path_file_text_3434_csv.exists()
    
    # check if header and content of files exist
    strings_expected = [
        f'That is a test {line_number}' for line_number in range(5)
        ]
    with open(str(path_file_text_3434_csv), 'r') as file_text_3434:
        for line_number, line_content in enumerate(file_text_3434, start = -1):
            if line_number == -1:
                assert line_content.rstrip() == 'HEADER'
            else:
                assert line_content.rstrip() in strings_expected
                
