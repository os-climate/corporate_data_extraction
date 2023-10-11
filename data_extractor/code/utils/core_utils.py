import os
from pathlib import Path
import shutil
import pandas as pd
from utils.s3_communication import S3Communication
from utils.settings import get_s3_settings, S3Settings

S3Settings = get_s3_settings()


source_annotation = ''
destination_annotation = ''
project_prefix = ''

def create_folder(path_folder_as_str: str) -> None:
    path_folder = Path(path_folder_as_str)
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

def convert_xls_to_csv(s3c_main: S3Communication, s3c_interim: S3Communication):
#def convert_xls_to_csv(path_source_folder: Path, path_destination_annotation_folder: Path):
    """
    This function transforms the annotations.xlsx file into annotations.csv.

    :param s3_usage: boolean: True if S3 connection should be used
    :param s3c_main: S3Communication class element (based on boto3)
    :param s3c_interim: S3Communication class element (based on boto3)
    return None
    """
    path_source_annotation_folder = Path(source_annotation)
    path_destination_annotation_folder = Path(destination_annotation)
    
    # download_data_from_s3_main_bucket_to_local_folder_if_required(s3c_main, path_source_annotation_folder)
        
    _convert_xls_to_csv(path_source_annotation_folder, path_destination_annotation_folder)
    
    # upload_data_from_local_folder_to_s3_interim_bucket_if_required(s3c_interim, path_destination_annotation_folder)

    
def _convert_xls_to_csv(path_source_annotation_folder: Path, path_destination_annotation_folder: Path):
    list_of_xlsx_files_in_source_folder = list(path_source_annotation_folder.glob('*.xlsx'))
    number_of_xlsx_files_in_source_folder = len(list_of_xlsx_files_in_source_folder)
    
    if number_of_xlsx_files_in_source_folder == 1:
        _convert_single_file_from_xls_to_csv(*list_of_xlsx_files_in_source_folder, path_destination_annotation_folder)
    elif number_of_xlsx_files_in_source_folder < 1:
        raise ValueError('No annotation excel sheet found')
    elif number_of_xlsx_files_in_source_folder > 1:
        raise ValueError('More than one excel sheet found')

def _convert_single_file_from_xls_to_csv(path_file: Path, path_destination_annotation_folder: Path) -> None:
    print('Converting ' + str(path_file) + ' to csv-format')
    read_file = pd.read_excel(path_file, engine='openpyxl')
    read_file.to_csv(path_destination_annotation_folder / 'aggregated_annotation.csv', index=None, header=True)
