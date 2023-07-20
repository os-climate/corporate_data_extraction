from pathlib import Path
import pytest
import config_path
from train_on_pdf import convert_xls_to_csv
from tests.utils_test import write_to_file, create_single_xlsx_file, create_multiple_xlsx_files
import shutil
from unittest.mock import patch, Mock
import train_on_pdf
import s3_communication
import pandas as pd


def mock_s3_download_single_file(*args, **kwargs):
    """Mock the download_files_in_prefix_to_dir method of the S3Communication object
    by creating a single xlsx file in path_folder_download_source"""
    return create_single_xlsx_file(Path(args[1]))

def mock_s3_download_multiple_files(*args, **kwargs):
    """Mock the download_files_in_prefix_to_dir method of the S3Communication object
    by creating a single xlsx file in path_folder_download_source"""
    return create_multiple_xlsx_files(Path(args[1]))


def mock_s3_upload_files(*args, **kwargs):
    """Mock the upload_files_in_dir_to_prefix method of the S3Communication object
    by creating a dummy function
    """
    def mock_s3_upload_files_return(*args, **kwargs):
        pass
            
    return mock_s3_upload_files_return(*args, **kwargs)

@pytest.fixture
def prerequisites_convert_xls_to_csv(path_temporary_folder: Path):
    """Defines a fixture for mocking all required objects, methods and functions

    :param path_temporary_folder: Requesting the temporary folder fixture
    :type path_temporary_folder: Path
    """
    path_source_annotation = path_temporary_folder / 'source_annotation'
    path_destination_annotation = path_temporary_folder / 'destination_annotation'
    path_source_annotation.mkdir(parents = True, exist_ok = True)
    path_destination_annotation.mkdir(parents = True, exist_ok = True)
    project_prefix = 'corporate_data_extraction_projects'
    s3_usage = False
    
    with (patch('train_on_pdf.source_annotation', str(path_source_annotation)),
          patch('train_on_pdf.destination_annotation', str(path_destination_annotation)),
          patch('train_on_pdf.project_prefix', project_prefix),
          patch('train_on_pdf.s3_usage', s3_usage),
          patch('train_on_pdf.s3c_main', Mock(spec = s3_communication.S3Communication)) as mock_s3c_main,
          patch('train_on_pdf.s3c_interim', Mock(spec = s3_communication.S3Communication)) as mock_s3c_interim):
        mock_s3c_main.download_files_in_prefix_to_dir.side_effect = mock_s3_download_single_file
        mock_s3c_interim.upload_files_in_dir_to_prefix.side_effect = mock_s3_upload_files
        yield
        
    # cleanup
    shutil.rmtree(path_temporary_folder)


def test_convert_xls_to_csv_download_s3(prerequisites_convert_xls_to_csv):
    """Tests the function convert_xls_to_csv for successfully downloading
    files from a S3 bucket. All required variables/functions/methods are mocked by the 
    prerequisites_convert_xls_to_csv fixture"""
    # set the name of the project
    project_name = 'TEST'
    
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(project_name)
    
    # assert that function has been called
    train_on_pdf.s3c_main.download_files_in_prefix_to_dir.assert_called_once()   
    # assert that files exists in source_annotation folder
    content_folder_source_annotation = list(Path(train_on_pdf.source_annotation).glob('*.xlsx'))
    assert len(content_folder_source_annotation) == 1 
              

def test_convert_xls_to_csv_upload_s3(prerequisites_convert_xls_to_csv):
    """Tests the function convert_xls_to_csv for successfully uploading
    files to a S3 bucket"""
    project_name = 'TEST'
    train_on_pdf.s3_usage = True
        
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(project_name)
    
    # assert upload function has been called
    train_on_pdf.s3c_interim.upload_files_in_dir_to_prefix.assert_called_once()
        

def test_convert_xls_to_csv_value_error_multiple_xls(prerequisites_convert_xls_to_csv):
    """Test the function convert_xls_to_csv for raising ValueError if more than one
    xlsx files exist"""
    project_name = 'TEST'
    
    # mock the function download_files_in_prefix_to_dir of the S3_Connection object
    train_on_pdf.s3c_main.download_files_in_prefix_to_dir.side_effect = mock_s3_download_multiple_files
    
    # perform the convert_xls_to_csv call and check for ValueError
    with pytest.raises(ValueError, match = 'More than one excel sheet found'):
        convert_xls_to_csv(project_name)
    # assert that function has been called
    train_on_pdf.s3c_main.download_files_in_prefix_to_dir.assert_called_once()


def test_convert_xls_to_csv_value_error_no_annotation_xls(prerequisites_convert_xls_to_csv):
    """Test the function convert_xls_to_csv for raising ValueError if no annotation xlsx files
    exist"""
    project_name = 'TEST'

    # mock the function download_files_in_prefix_to_dir of the S3_Connection object
    train_on_pdf.s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: None
    
    # perform the convert_xls_to_csv call and check for ValueError
    with pytest.raises(ValueError, match = 'No annotation excel sheet found'):
        convert_xls_to_csv(project_name)
    # assert that function has been called
    train_on_pdf.s3c_main.download_files_in_prefix_to_dir.assert_called_once()


def test_convert_xls_to_csv_s3_usage(prerequisites_convert_xls_to_csv):
    """Tests the function convert_xls_to_csv for actively using an S3 bucket"""
    project_name = 'TEST'
    train_on_pdf.s3_usage = True
        
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(project_name)
    
    # assert that s3_usage is True and upload_files_in_dir_to_prefix has been called
    assert train_on_pdf.s3_usage == True
    train_on_pdf.s3c_interim.upload_files_in_dir_to_prefix.assert_called_once()
    

def test_convert_xls_to_csv_no_s3_usage(prerequisites_convert_xls_to_csv):
    """Tests the function convert_xls_to_csv for not using an S3 bucket"""
    project_name = 'TEST'
    s3_usage = False
   
    # perform the convert_xls_to_csv call
    convert_xls_to_csv(project_name)
    
    # assert that s3_usage is True and upload_files_in_dir_to_prefix has been called
    assert train_on_pdf.s3_usage == False
    train_on_pdf.s3c_interim.upload_files_in_dir_to_prefix.assert_not_called()
