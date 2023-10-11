from pathlib import Path
import pytest
# from train_on_pdf import 
from tests.utils_test import write_to_file, create_single_xlsx_file, create_multiple_xlsx_files
import shutil
from unittest.mock import patch, Mock, MagicMock
import train_on_pdf
from utils.s3_communication import S3Communication
import utils.core_utils
from utils.core_utils import convert_xls_to_csv, _convert_xls_to_csv, _convert_single_file_from_xls_to_csv,\
download_data_from_s3_main_bucket_to_local_folder_if_required, upload_data_from_local_folder_to_s3_interim_bucket_if_required
import pandas as pd

from utils.settings import get_s3_settings
S3Settings = get_s3_settings()
# S3Settings.s3_usage = True


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