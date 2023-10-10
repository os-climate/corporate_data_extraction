from pathlib import Path
import pytest
# from train_on_pdf import 
from tests.utils_test import write_to_file, create_single_xlsx_file, create_multiple_xlsx_files
import shutil
from unittest.mock import patch, Mock, MagicMock
import train_on_pdf
from utils.s3_communication import S3Communication
import utils.core_utils
from utils.core_utils import convert_xls_to_csv, _convert_xls_to_csv, _convert_single_file_from_xls_to_csv
import pandas as pd

from utils.settings import get_s3_settings
S3Settings = get_s3_settings()


@pytest.fixture(autouse=True)
def paths_to_source_and_destination_annotation(path_folder_temporary: Path) -> None:
    """Defines a fixture for mocking all required objects, methods and functions

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :rtype: None
    """
    path_source_annotation = path_folder_temporary / 'input' / 'pdfs' / 'training'
    path_destination_annotation = path_folder_temporary / 'interim' / 'ml' / 'annotations'
    path_source_annotation.mkdir(parents = True, exist_ok = True)
    path_destination_annotation.mkdir(parents = True, exist_ok = True)
    
    with (patch('utils.core_utils.source_annotation', str(path_source_annotation)),
          patch('utils.core_utils.destination_annotation', str(path_destination_annotation)),
          patch.object(S3Settings, 'prefix', str(path_folder_temporary))):
        yield path_source_annotation, path_destination_annotation
        
        # cleanup
        for path in path_folder_temporary.glob("*"):
            shutil.rmtree(path)


def test_convert_xls_to_csv_download_s3(paths_to_source_and_destination_annotation):
    """Tests the function convert_xls_to_csv for successfully downloading
    files from a S3 bucket. All required variables/functions/methods are mocked by the 
    paths_to_source_and_destination_annotation fixture
    Requesting paths_to_source_and_destination_annotation automatically (autouse)
    """
    
    # s3_usage = True
    # mocked_s3c_main = Mock(spec=S3Communication)
    # mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_single_xlsx_file(Path(args[1]))
    # mocked_s3c_interim = Mock(spec=S3Communication)
    
    
    create_single_xlsx_file(paths_to_source_and_destination_annotation[0])
    # convert_xls_to_csv(s3_usage, mocked_s3c_main, mocked_s3c_interim)
    _convert_xls_to_csv(*paths_to_source_and_destination_annotation)
    
    # mocked_s3c_main.download_files_in_prefix_to_dir.assert_called_once()   
    content_folder_source_annotation = list(Path(utils.core_utils.source_annotation).glob('*.xlsx'))
    assert len(content_folder_source_annotation) == 1 
    
    
def test_convert_xls_to_csv_no_xls_files_found():
    
    mocked_path_source_annotation = Mock(spec=Path)
    mocked_path_source_annotation.glob.return_value = []
    mocked_path_destination_annotation = Mock(spec=Path)
    
    with pytest.raises(ValueError) as exception_info:
        _convert_xls_to_csv(mocked_path_source_annotation, mocked_path_destination_annotation)
        
    assert str(exception_info.value) == 'No annotation excel sheet found'
    

def test_convert_xls_to_csv_multiple_xls_files_found():
    
    mocked_path_source_annotation = Mock(spec=Path)
    mocked_path_source_annotation.glob.return_value = ['one.xlsx', 'two.xlsx']
    mocked_path_destination_annotation = Mock(spec=Path)
    
    with pytest.raises(ValueError) as exception_info:
        _convert_xls_to_csv(mocked_path_source_annotation, mocked_path_destination_annotation)
        
    assert str(exception_info.value) == 'More than one excel sheet found'
    

def test_convert_xls_to_csv_single_xls_file_found():
    
    mocked_path_source_annotation = Mock(spec=Path)
    mocked_path_source_annotation.glob.return_value = ['one.xlsx']
    mocked_path_destination_annotation = Mock(spec=Path)
    
    with patch('utils.core_utils._convert_single_file_from_xls_to_csv') as mocked_convert_function:
        _convert_xls_to_csv(mocked_path_source_annotation, mocked_path_destination_annotation)
    
    mocked_convert_function.assert_called_once()
    

def test_convert_single_file_from_xls_to_csv():
    mocked_path_file = Mock(spec=Path)
    mocked_path_destination_annotation_folder = MagicMock(spec=Path)
    # using MagicMock to replace __truediv__ using by pathlib.Path 
    mocked_path_destination_annotation_folder.__truediv__.return_value = 'file_output.csv'
    
    with patch('utils.core_utils.pd') as mocked_pandas:
        _convert_single_file_from_xls_to_csv(mocked_path_file, mocked_path_destination_annotation_folder)
    
    mocked_pandas.read_excel.assert_called_with(mocked_path_file, engine='openpyxl')
    mocked_pandas.read_excel.return_value.to_csv.assert_called_with('file_output.csv', index=None, header=True)
    

def test_convert_xls_to_csv_upload_s3():
    """Tests the function convert_xls_to_csv for successfully uploading
    files to a S3 bucket
    Requesting paths_to_source_and_destination_annotation automatically (autouse)
    """
    S3Settings.s3_usage = True
    mocked_s3c_main = Mock(spec=S3Communication)
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_single_xlsx_file(Path(args[1]))
    mocked_s3c_interim = Mock(spec=S3Communication)
    mocked_s3c_interim.upload_files_in_dir_to_prefix.side_effect = lambda *args: create_multiple_xlsx_files(Path(args[1]))
        
    convert_xls_to_csv(mocked_s3c_main, mocked_s3c_interim)
    
    mocked_s3c_interim.upload_files_in_dir_to_prefix.assert_called_once()
        

def test_convert_xls_to_csv_value_error_multiple_xls():
    """Test the function convert_xls_to_csv for raising ValueError if more than one
    xlsx files exist
    Requesting paths_to_source_and_destination_annotation automatically (autouse)
    """
    S3Settings.s3_usage = True
    mocked_s3c_main = Mock(spec=S3Communication)
    # create more than one file executing mocked_s3c_main
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_multiple_xlsx_files(Path(args[1]))
    mocked_s3c_interim = Mock(spec=S3Communication)
    
    with pytest.raises(ValueError, match = 'More than one excel sheet found'):
        convert_xls_to_csv(mocked_s3c_main, mocked_s3c_interim)

    mocked_s3c_main.download_files_in_prefix_to_dir.assert_called_once()


def test_convert_xls_to_csv_value_error_no_annotation_xls():
    """Test the function convert_xls_to_csv for raising ValueError if no annotation xlsx files
    exist
    Requesting paths_to_source_and_destination_annotation automatically (autouse)
    """
    S3Settings.s3_usage = True
    mocked_s3c_main = Mock(spec=S3Communication)
    # do not create any file
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: None
    mocked_s3c_interim = Mock(spec=S3Communication)
    
    with pytest.raises(ValueError, match = 'No annotation excel sheet found'):
        convert_xls_to_csv(mocked_s3c_main, mocked_s3c_interim)
        
    mocked_s3c_main.download_files_in_prefix_to_dir.assert_called_once()


def test_convert_xls_to_csv_s3_usage():
    """Tests the function convert_xls_to_csv for actively using an S3 bucket
    Requesting paths_to_source_and_destination_annotation automatically (autouse)
    """
    S3Settings.s3_usage = True
    mocked_s3c_main = Mock(spec=S3Communication)
    mocked_s3c_main.download_files_in_prefix_to_dir.side_effect = lambda *args: create_single_xlsx_file(Path(args[1]))
    mocked_s3c_interim = Mock(spec=S3Communication)
    mocked_s3c_interim.upload_files_in_dir_to_prefix.side_effect = lambda *args: create_multiple_xlsx_files(Path(args[1]))
        
    convert_xls_to_csv(mocked_s3c_main, mocked_s3c_interim)
    
    mocked_s3c_interim.upload_files_in_dir_to_prefix.assert_called_once()
    

def test_convert_xls_to_csv_no_s3_usage():
    """Tests the function convert_xls_to_csv for not using an S3 bucket
    Requesting paths_to_source_and_destination_annotation automatically (autouse)
    """
    S3Settings.s3_usage = False
    mocked_s3c_main = Mock(spec=S3Communication)
    mocked_s3c_interim = Mock(spec=S3Communication)
   
    with pytest.raises(ValueError, match = 'No annotation excel sheet found'):
        convert_xls_to_csv(mocked_s3c_main, mocked_s3c_interim)
    
    mocked_s3c_interim.upload_files_in_dir_to_prefix.assert_not_called()
