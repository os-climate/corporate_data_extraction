from pathlib import Path
import config_path
from train_on_pdf import link_files, link_extracted_files
import shutil

def test_link_files(path_temporary_folder: Path):
    """Tests if link_files creates proper hard links"""
    path_folder_source = path_temporary_folder / 'source'
    path_folder_destination = path_temporary_folder / 'destination'
    path_folder_source.mkdir(parents = True)
    path_folder_destination.mkdir(parents = True)
    
    # create sample files
    for i in range(10):
        path_current_file = path_folder_source / f'test_{i}.txt'
        path_current_file.touch()
    
    # perform the linking
    link_files(str(path_folder_source), str(path_folder_destination))
    
    # check for hard links
    for i in range(10):
        path_current_file = path_folder_source / f'test_{i}.txt'
        assert path_current_file.stat().st_nlink == 2

    # cleanup
    shutil.rmtree(path_temporary_folder)

def test_link_extracted_files_result(path_temporary_folder: Path):
    """Test if link_extracted_files returns True if executed"""
    # create test folders
    path_source_extraction = path_temporary_folder / 'source_extraction'
    path_source_pdf = path_temporary_folder / 'source_pdf'
    path_destination_extraction = path_temporary_folder / 'destination_extraction'
    path_source_extraction.mkdir(parents = True)
    path_source_pdf.mkdir(parents = True)
    path_destination_extraction.mkdir(parents = True)
    
    # single pdf and json file 
    path_source_extraction_file_pdf = path_source_extraction / f'test.pdf'
    path_source_extraction_file_json = path_source_extraction / f'test.json'
    path_source_file_pdf = path_source_pdf / f'test.pdf'
    
    result = link_extracted_files(str(path_source_extraction), str(path_source_pdf),
                                  str(path_destination_extraction))
    assert result == True
    
    # cleanup
    shutil.rmtree(path_temporary_folder)
    
    
def test_link_extracted_files_copy(path_temporary_folder: Path):
    """Test if the extracted json files in folder_source_extraction has a
    regarding pdf in the folder_source_pdf and if so, copy the json file to
    the folder_destination_extraction"""
    # create test folders
    path_source_extraction = path_temporary_folder / 'source_extraction'
    path_source_pdf = path_temporary_folder / 'source_pdf'
    path_destination_extraction = path_temporary_folder / 'destination_extraction'
    path_source_extraction.mkdir(parents = True)
    path_source_pdf.mkdir(parents = True)
    path_destination_extraction.mkdir(parents = True)
    
    # create test pdf and json files in the source_extraction and source_pdf folders
    for i in range(10):
        path_current_file = path_source_extraction / f'test_{i}.pdf'
        path_current_file.touch()
        path_current_file = path_source_extraction / f'test_{i}.json'
        path_current_file.touch()
        path_current_file = path_source_pdf / f'test_{i}.pdf'
        path_current_file.touch()
        
    # check if no files exist in the destination_extraction folder
    for i in range(10):
        path_current_file = path_destination_extraction / f'test_{i}.json'
        assert not path_current_file.exists() == True
    
    # perform extracted file linking
    link_extracted_files(str(path_source_extraction), str(path_source_pdf),
                                  str(path_destination_extraction))
    
    # check if files exist in the destination_extraction folder
    for i in range(10):
        path_current_file = path_destination_extraction / f'test_{i}.json'
        assert path_current_file.exists() == True
        
    # cleanup
    shutil.rmtree(path_temporary_folder)
