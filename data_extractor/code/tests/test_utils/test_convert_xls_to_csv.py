from pathlib import Path
import pytest
from unittest.mock import patch, Mock
from utils.xls_to_csv_converter import XlsToCsvConverter, AnnotationConversionError

 
@pytest.fixture
def converter() -> XlsToCsvConverter:
    return XlsToCsvConverter(Path('source_folder'), Path('destination_folder'))

def test_convert_method_called(converter):
    list_paths_sample: list[Path] = [Path()]
    mocked_find_files: Mock = Mock(return_value=list_paths_sample)
    mocked_check_xlsx_files: Mock = Mock()
    mocked_check_valid_paths: Mock = Mock()
    mocked_convert_file: Mock = Mock()
    
    with (patch.object(converter, '_find_xlsx_files_in_source_folder', mocked_find_files),
          patch.object(converter, '_check_xlsx_files', mocked_check_xlsx_files),
          patch.object(converter, '_check_for_valid_paths', mocked_check_valid_paths),
          patch.object(converter, '_convert_single_file_to_csv', mocked_convert_file)):
        converter.convert()

    mocked_find_files.assert_called_once()
    mocked_check_xlsx_files.assert_called_once_with(list_paths_sample)
    mocked_check_valid_paths.assert_called_once()
    mocked_convert_file.assert_called_once_with(list_paths_sample[0])

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
        list_paths_xlsx_files: list[Path] = converter._find_xlsx_files_in_source_folder()

    mocked_path_glob.assert_called_once_with('*.xlsx')
    assert list_paths_xlsx_files == [Path('file1.xlsx'), Path('file2.xlsx')]
    

def test_check_xlsx_files_single_file(converter):
    list_paths_xlsx_files = [Path('file.xlsx')]

    try:
        converter._check_xlsx_files(list_paths_xlsx_files)
    except Exception as e:
        pytest.fail(f"An unexpected exception occurred: {e}")

def test_check_xlsx_files_no_files(converter):
    list_paths_xlsx_files = []

    with pytest.raises(AnnotationConversionError):
        converter._check_xlsx_files(list_paths_xlsx_files)

def test_check_xlsx_files_multiple_files(converter):
    list_paths_xlsx_files = [Path('file1.xlsx'), Path('file2.xlsx')]

    with pytest.raises(AnnotationConversionError):
        converter._check_xlsx_files(list_paths_xlsx_files)
        
def test_check_for_valid_path_source_folder(converter):
    converter._path_source_folder = Path()
    
    with pytest.raises(AnnotationConversionError):
        converter._check_for_valid_paths()

def test_check_for_valid_path_destination_folder(converter):
    converter._path_destination_folder = Path()
    
    with pytest.raises(AnnotationConversionError):
        converter._check_for_valid_paths()
