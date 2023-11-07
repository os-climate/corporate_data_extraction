from pathlib import Path
import pandas as pd
from utils.exceptions import AnnotationConversionError

class Converter:
    def convert(self) -> None:
        pass

class XlsToCsvConverter(Converter):
    def __init__(self, path_folder_source: Path = Path(), 
                 path_folder_destination: Path = Path()):
        self.path_folder_source: Path = path_folder_source
        self.path_folder_destination: Path = path_folder_destination

    @property
    def path_folder_source(self) -> Path:
        return self._path_folder_source
    
    @path_folder_source.setter
    def path_folder_source(self, path: Path) -> None:
        if isinstance(path, Path):
            self._path_folder_source: Path = path
        else:
            raise TypeError(f'{path} is of type {type(path)}, not of type Path')
    
    @property
    def path_folder_destination(self) -> Path:
        return self._path_folder_destination

    @path_folder_destination.setter
    def path_folder_destination(self, path: Path) -> None:
        if isinstance(path, Path):
            self._path_folder_destination: Path = path
        else:
            raise TypeError(f'{path} is of type {type(path)}, not of type Path')
        
    def convert(self) -> None:
        list_paths_xlsx_files: list[Path] = self._find_xlsx_files_in_source_folder()
        self._check_xlsx_files(list_paths_xlsx_files)
        self._check_for_valid_paths()
        self._convert_single_file_to_csv(list_paths_xlsx_files[0])

    def _find_xlsx_files_in_source_folder(self) -> list[Path]:
        list_paths_xlsx_files: list[Path] = list(self._path_folder_source.glob('*.xlsx'))
        return list_paths_xlsx_files
    
    def _check_for_valid_paths(self) -> None:
        if self._path_folder_source.name == '':
            raise AnnotationConversionError('No source folder path set')
        if self._path_folder_destination.name == '':
            raise AnnotationConversionError('No destination folder path set')

    def _check_xlsx_files(self, list_paths_xlsx_files: list[Path]) -> None:
        if len(list_paths_xlsx_files) < 1:
            raise AnnotationConversionError('No annotation excel sheet found')
        elif len(list_paths_xlsx_files) > 1:
            raise AnnotationConversionError('More than one excel sheet found')

    def _convert_single_file_to_csv(self, path_file: Path) -> None:
        print(f'Converting {path_file} to csv-format')
        df_read_excel: pd.DataFrame = pd.read_excel(path_file, engine='openpyxl')
        path_csv_file: Path = self._path_folder_destination / 'aggregated_annotation.csv'
        df_read_excel.to_csv(path_csv_file, index=None, header=True)
