import os
from pathlib import Path
import shutil
import pandas as pd


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


# def convert_xls_to_csv(s3_usage, s3c_main, s3c_interim):
def convert_xls_to_csv(path_source_folder: Path, path_destination_annotation_folder: Path):
    """
    This function transforms the annotations.xlsx file into annotations.csv.

    :param s3_usage: boolean: True if S3 connection should be used
    :param s3c_main: S3Communication class element (based on boto3)
    :param s3c_interim: S3Communication class element (based on boto3)
    return None
    """
    # if s3_usage:
    #     s3c_main.download_files_in_prefix_to_dir(project_prefix + '/input/annotations',
    #                                              path_source_folder)
        
    list_of_xlsx_files_in_source_folder = list(path_source_folder.glob('*.xlsx'))
    number_of_xlsx_files_in_source_folder = len(list_of_xlsx_files_in_source_folder)
    
    if number_of_xlsx_files_in_source_folder == 1:
        _convert_file_from_xls_to_csv(*list_of_xlsx_files_in_source_folder, path_destination_annotation_folder)
    elif number_of_xlsx_files_in_source_folder < 1:
        raise ValueError('No annotation excel sheet found')
    elif number_of_xlsx_files_in_source_folder > 1:
        raise ValueError('More than one excel sheet found')
        
    # first = True
    # for path_file in path_source_folder.iterdir():
    #     if path_file.suffix == '.xlsx':
    #         if not first:
    #             raise ValueError('More than one excel sheet found')
    #         print('Converting ' + str(path_file) + ' to csv-format')
    #         # only reads first sheet in excel file
    #         read_file = pd.read_excel(path_file, engine='openpyxl')
    #         read_file.to_csv(path_destination_annotation_folder / 'aggregated_annotation.csv', index=None, header=True)
    #         # if s3_usage:
    #         #     s3c_interim.upload_files_in_dir_to_prefix(path_destination_annotation_folder, 
    #         #                                               project_prefix + '/interim/ml/annotations')
    #         first = False         
    # if first:
    #     raise ValueError('No annotation excel sheet found')
    
def _convert_file_from_xls_to_csv(path_file: Path, path_destination_annotation_folder: Path) -> None:
    print('Converting ' + str(path_file) + ' to csv-format')
    read_file = pd.read_excel(path_file, engine='openpyxl')
    read_file.to_csv(path_destination_annotation_folder / 'aggregated_annotation.csv', index=None, header=True)
