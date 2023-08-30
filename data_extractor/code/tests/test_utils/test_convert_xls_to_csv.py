from pathlib import Path
import pytest
from train_on_pdf import convert_xls_to_csv
from tests.utils_test import write_to_file, create_single_xlsx_file, create_multiple_xlsx_files
import shutil
from unittest.mock import patch, Mock
import train_on_pdf
import s3_communication
import pandas as pd


@pytest.fixture(autouse=True)
def prerequisites_convert_xls_to_csv(path_folder_temporary: Path) -> None:
    """Defines a fixture for mocking all required objects, methods and functions

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :rtype: None
    """
    path_source_annotation = path_folder_temporary / 'input' / 'pdfs' / 'training'
    path_destination_annotation = path_folder_temporary / 'interim' / 'ml' / 'annotations'
    path_source_annotation.mkdir(parents = True, exist_ok = True)
    path_destination_annotation.mkdir(parents = True, exist_ok = True)
    project_prefix = 'corporate_data_extraction_projects'
    
    with (patch('train_on_pdf.source_annotation', str(path_source_annotation)),
          patch('train_on_pdf.destination_annotation', str(path_destination_annotation)),
          patch('train_on_pdf.project_prefix', project_prefix)): 
        yield
        
        # cleanup
        for path in path_folder_temporary.glob("*"):
            shutil.rmtree(path)


def test_convert_xls_to_csv_download_s3():
    """Tests the function convert_xls_to_csv for successfully downloading
    files from a S3 bucket. All required variables/functions/methods are mocked by the 
    prerequisites_convert_xls_to_csv fixture
    Requesting prerequisites_convert_xls_to_csv automatically (autouse)
    """
    
    s3_usage = True
    mocked_s3c_main = Mock(spec = s3_communication.S3Communication)
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_single_xlsx_file(Path(args[1]))
    mocked_s3c_interim = Mock(spec = s3_communication.S3Communication)
    
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    
    # assert that function has been called
    mocked_s3c_main.download_files_in_prefix_to_dir.assert_called_once()   
    # assert that files exists in source_annotation folder
    content_folder_source_annotation = list(Path(train_on_pdf.source_annotation).glob('*.xlsx'))
    assert len(content_folder_source_annotation) == 1 
              

def test_convert_xls_to_csv_upload_s3():
    """Tests the function convert_xls_to_csv for successfully uploading
    files to a S3 bucket
    Requesting prerequisites_convert_xls_to_csv automatically (autouse)
    """
    s3_usage = True
    mocked_s3c_main = Mock(spec = s3_communication.S3Communication)
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_single_xlsx_file(Path(args[1]))
    mocked_s3c_interim = Mock(spec = s3_communication.S3Communication)
    mocked_s3c_interim.upload_files_in_dir_to_prefix.side_effect = lambda *args: create_multiple_xlsx_files(Path(args[1]))
        
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    
    # assert upload function has been called
    mocked_s3c_interim.upload_files_in_dir_to_prefix.assert_called_once()
        

def test_convert_xls_to_csv_value_error_multiple_xls():
    """Test the function convert_xls_to_csv for raising ValueError if more than one
    xlsx files exist
    Requesting prerequisites_convert_xls_to_csv automatically (autouse)
    """
    s3_usage = True
    mocked_s3c_main = Mock(spec = s3_communication.S3Communication)
    # create more than one file executing mocked_s3c_main
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_multiple_xlsx_files(Path(args[1]))
    mocked_s3c_interim = Mock(spec = s3_communication.S3Communication)
    
    # perform the convert_xls_to_csv call and check for ValueError
    with pytest.raises(ValueError, match = 'More than one excel sheet found'):
        convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    # assert that function has been called
    mocked_s3c_main.download_files_in_prefix_to_dir.assert_called_once()


def test_convert_xls_to_csv_value_error_no_annotation_xls():
    """Test the function convert_xls_to_csv for raising ValueError if no annotation xlsx files
    exist
    Requesting prerequisites_convert_xls_to_csv automatically (autouse)
    """
    s3_usage = True
    mocked_s3c_main = Mock(spec = s3_communication.S3Communication)
    # do not create any file
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: None
    mocked_s3c_interim = Mock(spec = s3_communication.S3Communication)
    
    # perform the convert_xls_to_csv call and check for ValueError
    with pytest.raises(ValueError, match = 'No annotation excel sheet found'):
        convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    # assert that function has been called
    mocked_s3c_main.download_files_in_prefix_to_dir.assert_called_once()


def test_convert_xls_to_csv_s3_usage():
    """Tests the function convert_xls_to_csv for actively using an S3 bucket
    Requesting prerequisites_convert_xls_to_csv automatically (autouse)
    """
    s3_usage = True
    mocked_s3c_main = Mock(spec = s3_communication.S3Communication)
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_single_xlsx_file(Path(args[1]))
    mocked_s3c_interim = Mock(spec = s3_communication.S3Communication)
    mocked_s3c_interim.upload_files_in_dir_to_prefix.side_effect = lambda *args: create_multiple_xlsx_files(Path(args[1]))
        
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    
    # assert that s3_usage is True and upload_files_in_dir_to_prefix has been called
    mocked_s3c_interim.upload_files_in_dir_to_prefix.assert_called_once()
    

def test_convert_xls_to_csv_no_s3_usage():
    """Tests the function convert_xls_to_csv for not using an S3 bucket
    Requesting prerequisites_convert_xls_to_csv automatically (autouse)
    """
    s3_usage = False
    mocked_s3c_main = Mock(spec = s3_communication.S3Communication)
    mocked_s3c_interim = Mock(spec = s3_communication.S3Communication)
   
    # perform the convert_xls_to_csv call and check for ValueError
    with pytest.raises(ValueError, match = 'No annotation excel sheet found'):
        convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    
    # assert that s3_usage is True and upload_files_in_dir_to_prefix has been called
    mocked_s3c_interim.upload_files_in_dir_to_prefix.assert_not_called()
