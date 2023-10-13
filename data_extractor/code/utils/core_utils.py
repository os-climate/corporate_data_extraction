import os
from pathlib import Path
import shutil
import pandas as pd
from utils.s3_communication import S3Communication
from utils.settings import get_s3_settings, S3Settings

S3Settings = get_s3_settings()


def create_folder(path_folder: Path) -> None:
    try:
        path_folder.mkdir()
    except OSError:
        _delete_files_in_folder(path_folder)
    except FileNotFoundError:
        print('No valid path given')

            
def _delete_files_in_folder(path_folder: Path) -> None:
    for path_file_current in path_folder.iterdir():
        _delete_file(path_file_current)
      
  
def _delete_file(path_file: Path) -> None:
    try:
        path_file.unlink()
    except Exception as exception:
        print('Failed to delete %s. Reason: %s' % (str(path_file), exception))
                

def copy_file_without_overwrite(path_folder_source_as_str: str, path_folder_destination_as_str: str) -> bool:
    path_folder_source = Path(path_folder_source_as_str)
    path_folder_destination = Path(path_folder_destination_as_str)
    
    for path_file_current_source in path_folder_source.iterdir():
        path_file_current_destination = path_folder_destination / path_file_current_source.name
        if not path_file_current_destination.exists():
            shutil.copyfile(path_file_current_source, path_file_current_destination)
    return True


class S3Controller():
    
    def __init__(self, 
                 main_bucket: S3Communication, 
                 interim_bucket: S3Communication,
                 settings: S3Settings):
        self.main_bucked = main_bucket
        self.interim_bucket = interim_bucked
        self.settings = settings
        
    def _create_prefix_path_for_download_in_s3(self):
        self.path_prefix_for_download_3 = self.settings.prefix / 'input' / 'annotations'

    def download_data_from_s3_main_bucket_to_local_folder_if_required(self):
        
        path_with_prefix_in_s3 = self.settings + '/input/annotations'
        path_source_folder = source_annotation
        
        if S3Settings.s3_usage:
            s3_bucket.download_files_in_prefix_to_dir(path_with_prefix_in_s3, 
                                                    path_source_folder)
    

    def upload_data_from_local_folder_to_s3_interim_bucket_if_required(self):
        
        path_destination_annotation_folder = destination_annotation
        path_with_prefix_in_s3 = S3Settings.prefix + '/interim/ml/annotations'
        
        if S3Settings.s3_usage:
            s3_bucket.upload_files_in_dir_to_prefix(path_destination_annotation_folder, 
                                                    path_with_prefix_in_s3)


def download_data_from_s3_main_bucket_to_local_folder_if_required(s3_bucket: S3Communication,
                                                                  path_s3_with_prefix_folder: Path,
                                                                  path_local_folder: Path):
    if S3Settings.s3_usage:
        s3_bucket.download_files_in_prefix_to_dir(path_s3_with_prefix_folder, 
                                                  path_local_folder)


def upload_data_from_local_folder_to_s3_interim_bucket_if_required(s3_bucket: S3Communication,
                                                                   path_local_folder: Path,
                                                                   path_s3_with_prefix_folder: Path):
    if S3Settings.s3_usage:
        s3_bucket.upload_files_in_dir_to_prefix(path_local_folder, 
                                                path_s3_with_prefix_folder) 

# def convert_xls_to_csv(path_source_annotation_folder: Path, 
#                        path_destination_annotation_folder: Path) -> None:
#     _convert_xls_to_csv(path_source_annotation_folder, path_destination_annotation_folder)
    
# def _convert_xls_to_csv(path_source_annotation_folder: Path, path_destination_annotation_folder: Path):
#     list_of_xlsx_files_in_source_folder = list(path_source_annotation_folder.glob('*.xlsx'))
#     number_of_xlsx_files_in_source_folder = len(list_of_xlsx_files_in_source_folder)
    
#     if number_of_xlsx_files_in_source_folder == 1:
#         _convert_single_file_from_xls_to_csv(*list_of_xlsx_files_in_source_folder, path_destination_annotation_folder)
#     elif number_of_xlsx_files_in_source_folder < 1:
#         raise ValueError('No annotation excel sheet found')
#     elif number_of_xlsx_files_in_source_folder > 1:
#         raise ValueError('More than one excel sheet found')

# def _convert_single_file_from_xls_to_csv(path_file: Path, path_destination_annotation_folder: Path) -> None:
#     print('Converting ' + str(path_file) + ' to csv-format')
#     read_file = pd.read_excel(path_file, engine='openpyxl')
#     read_file.to_csv(path_destination_annotation_folder / 'aggregated_annotation.csv', index=None, header=True)


class XlsToCsvConverter:
    def __init__(self, path_source_folder: Path | None = None, 
                 path_destination_folder: Path | None = None):
        self._path_source_folder = path_source_folder
        self._path_destination_folder = path_destination_folder

    def set_path_source_folder(self, path_source_folder: Path):
        self._path_source_folder = path_source_folder
        
    def set_path_destination_folder(self, path_destination_folder: Path):
        self._path_destination_folder = path_destination_folder
        
    def convert(self) -> None:
        list_paths_xlsx_files = self._find_xlsx_files_in_source_folder()
        self._validate_xlsx_files(list_paths_xlsx_files)
        self._check_for_valid_paths()
        self._convert_single_file_to_csv(xlsx_files[0])

    def _find_xlsx_files_in_source_folder(self) -> list[Path]:
        list_paths_xlsx_files = list(self._path_source_folder.glob('*.xlsx'))
        return list_paths_xlsx_files
    
    def _check_for_valid_paths(self) -> None:
        if self._path_source_folder is None:
            raise AnnotationConversionError('No source folder path set')
        if self._path_destination_folder is None:
            raise AnnotationConversionError('No source folder path set')

    def _validate_xlsx_files(self, list_paths_xlsx_files: list[Path]) -> None:
        if len(list_paths_xlsx_files) < 1:
            raise AnnotationConversionError('No annotation excel sheet found')
        elif len(list_paths_xlsx_files) > 1:
            raise AnnotationConversionError('More than one excel sheet found')

    def _convert_single_file_to_csv(self, path_file: Path) -> None:
        print(f'Converting {path_file} to csv-format')
        df_read_excel = pd.read_excel(path_file, engine='openpyxl')
        path_csv_file = self._path_destination_folder / 'aggregated_annotation.csv'
        df_read_excel.to_csv(path_csv_file, index=None, header=True)

class AnnotationConversionError(Exception):
    pass