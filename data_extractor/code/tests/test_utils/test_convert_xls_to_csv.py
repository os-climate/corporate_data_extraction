from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock
import utils.core_utils
import pandas as pd
# from utils.core_utils import convert_xls_to_csv, _convert_xls_to_csv, _convert_single_file_from_xls_to_csv
from utils.core_utils import XlsToCsvConverter, AnnotationConversionError
from utils.settings import get_s3_settings
S3Settings = get_s3_settings()
# S3Settings.s3_usage = True

    
# def test_convert_xls_to_csv_no_xls_files_found():
    
#     mocked_path_source_annotation = Mock(spec=Path)
#     mocked_path_source_annotation.glob.return_value = []
#     mocked_path_destination_annotation = Mock(spec=Path)
    
#     with pytest.raises(ValueError) as exception_info:
#         _convert_xls_to_csv(mocked_path_source_annotation, mocked_path_destination_annotation)
        
#     assert str(exception_info.value) == 'No annotation excel sheet found'
    

# def test_convert_xls_to_csv_multiple_xls_files_found():
    
#     mocked_path_source_annotation = Mock(spec=Path)
#     mocked_path_source_annotation.glob.return_value = ['one.xlsx', 'two.xlsx']
#     mocked_path_destination_annotation = Mock(spec=Path)
    
#     with pytest.raises(ValueError) as exception_info:
#         _convert_xls_to_csv(mocked_path_source_annotation, mocked_path_destination_annotation)
        
#     assert str(exception_info.value) == 'More than one excel sheet found'
    

# def test_convert_xls_to_csv_single_xls_file_found():
    
#     mocked_path_source_annotation = Mock(spec=Path)
#     mocked_path_source_annotation.glob.return_value = ['one.xlsx']
#     mocked_path_destination_annotation = Mock(spec=Path)
    
#     with patch('utils.core_utils._convert_single_file_from_xls_to_csv') as mocked_convert_function:
#         _convert_xls_to_csv(mocked_path_source_annotation, mocked_path_destination_annotation)
    
#     mocked_convert_function.assert_called_once()
    

# def test_convert_single_file_from_xls_to_csv():
#     mocked_path_file = Mock(spec=Path)
#     mocked_path_destination_annotation_folder = MagicMock(spec=Path)
#     # using MagicMock to replace __truediv__ using by pathlib.Path 
#     mocked_path_destination_annotation_folder.__truediv__.return_value = 'file_output.csv'
    
#     with patch('utils.core_utils.pd') as mocked_pandas:
#         _convert_single_file_from_xls_to_csv(mocked_path_file, mocked_path_destination_annotation_folder)
    
#     mocked_pandas.read_excel.assert_called_with(mocked_path_file, engine='openpyxl')
#     mocked_pandas.read_excel.return_value.to_csv.assert_called_with('file_output.csv', index=None, header=True)


# def test_convert_xls_to_csv_lower_abstraction_called():
#     mocked_path_source_annotation_folder = Mock(spec=Path)
#     mocked_path_destination_annotation_folder = Mock(spec=Path)
    
#     with patch('utils.core_utils._convert_xls_to_csv') as mocked_abstraction:
#         convert_xls_to_csv(mocked_path_source_annotation_folder, mocked_path_destination_annotation_folder)
        
#     mocked_abstraction.assert_called_with(mocked_path_source_annotation_folder,
#                                           mocked_path_destination_annotation_folder)

@pytest.fixture
def converter():
    return XlsToCsvConverter(Path('source_folder'), Path('destination_folder'))


def test_convert_single_file_to_csv(converter):
    mocked_read_excel = Mock()
    path_destination_folder = Path('destination_folder')
    
    with patch('utils.core_utils.pd.read_excel', mocked_read_excel):
        converter._convert_single_file_to_csv(Path('file.xlsx'))

    mocked_read_excel.assert_called_once_with(Path('file.xlsx'), engine='openpyxl')
    path_destination_file = path_destination_folder / 'aggregated_annotation.csv'
    mocked_read_excel.return_value.to_csv.assert_called_once_with(path_destination_file, index=None, header=True)


def test_find_xlsx_files_in_source_folder(converter):
    mocked_path_glob = Mock()
    mocked_path_glob.return_value = [Path('file1.xlsx'), Path('file2.xlsx')]

    with patch('utils.core_utils.Path.glob', mocked_path_glob):
        list_paths_xlsx_files = converter._find_xlsx_files_in_source_folder()

    mocked_path_glob.assert_called_once_with('*.xlsx')
    assert list_paths_xlsx_files == [Path('file1.xlsx'), Path('file2.xlsx')]
    

def test_validate_xlsx_files_single_file(converter):
    list_paths_xlsx_files = [Path('file.xlsx')]

    try:
        converter._validate_xlsx_files(list_paths_xlsx_files)
    except Exception as e:
        pytest.fail(f"An unexpected exception occurred: {e}")

def test_validate_xlsx_files_no_files(converter):
    list_paths_xlsx_files = []

    with pytest.raises(AnnotationConversionError):
        converter._validate_xlsx_files(list_paths_xlsx_files)

def test_validate_xlsx_files_multiple_files(converter):
    list_paths_xlsx_files = [Path('file1.xlsx'), Path('file2.xlsx')]

    with pytest.raises(AnnotationConversionError):
        converter._validate_xlsx_files(list_paths_xlsx_files)
        
def test_check_for_valid_path_source_folder(converter):
    converter._path_source_folder = None
    
    with pytest.raises(AnnotationConversionError):
        converter._check_for_valid_paths()

def test_check_for_valid_path_destination_folder(converter):
    converter._path_destination_folder = None
    
    with pytest.raises(AnnotationConversionError):
        converter._check_for_valid_paths()
