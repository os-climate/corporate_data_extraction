from pathlib import Path
from utils.helpers import create_tmp_file_path
from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings
from utils.settings import Settings, MainSettings

path_file_running = create_tmp_file_path()


class ProjectPaths(BaseSettings):
    _path_project_data_folder: Path
    _path_project_model_folder: Path
    _main_settings: Settings
    
    path_folder_source_pdf: Path = Field(default=Path('input/pdfs/training'))
    path_folder_source_annotation: Path = Field(default=Path('input/annotations'))
    path_folder_source_mapping: Path = Field(default=Path('input/kpi_mapping'))
    path_folder_destination_pdf: Path = Field(default=Path('interim/pdfs'))
    path_folder_destination_annotation: Path = Field(default=Path('interim/ml/annotations'))
    path_folder_destination_mapping: Path = Field(default=Path('interim/kpi_mapping'))
    path_folder_destination_extraction: Path = Field(default=Path('interim/ml/extraction'))
    path_folder_destination_curation: Path = Field(default=Path('interim/ml/curation'))
    path_folder_destination_training: Path = Field(default=Path('interim/ml/training'))

    path_folder_destination_saved_models_relevance: Path = Field(default=Path('RELEVANCE/Text'))
    path_folder_destination_saved_models_inference: Path = Field(default=Path('KPI_EXTRACTION/Text'))
    
    path_folder_text_3434: Path = Field(default=Path('interim/ml'))
    path_folder_relevance: Path = Field(default=Path('output/RELEVANCE/Text'))

    def __init__(self, 
                 path_project_data_folder: Path, 
                 path_project_model_folder: Path,
                 main_settings: Settings,
                 **kwargs):
        super().__init__(**kwargs)
        self._path_project_data_folder: Path = path_project_data_folder
        self._path_project_model_folder: Path = path_project_model_folder
        self._main_settings: Settings = main_settings
    
    @property
    def path_project_data_folder(self) -> Path:
        return self._path_project_data_folder
    
    @path_project_data_folder.setter
    def path_project_data_folder(self, path_new_project_data_folder: Path) -> None:
        self._path_project_data_folder: Path = path_new_project_data_folder

        for path_field in self.model_fields.keys():
            if 'saved_models' not in path_field:
                path_field_default: Path = self.model_fields[path_field].default
                setattr(self, f'{path_field}', path_new_project_data_folder / path_field_default)
    
    @property
    def path_project_model_folder(self) -> Path:
        return self._path_project_model_folder
    
    @path_project_model_folder.setter
    def path_project_model_folder(self, path_new_project_model_folder: Path) -> None:
        self._path_project_model_folder: Path = path_new_project_model_folder
        self._update_all_paths_depending_on_path_project_model_folder()

    @property
    def main_settings(self) -> Settings:
        return self._main_settings
    
    @main_settings.setter
    def main_settings(self, main_settings_new: Settings) -> None:
        self._main_settings: Settings = main_settings_new
        self._update_all_paths_depending_on_path_project_model_folder()

    def _update_all_paths_depending_on_path_project_model_folder(self) -> None:
        list_string_paths_depending_on_path_project_model_folder: list[str] = [
            'path_folder_destination_saved_models_relevance',
            'path_folder_destination_saved_models_inference']
        list_paths_main_settings: list[Path] = [Path(self._main_settings.train_relevance.output_model_name),
                                                Path(self._main_settings.train_kpi.output_model_name)]
        
        for string_model_field, path_main_settings in zip(list_string_paths_depending_on_path_project_model_folder,
                                                          list_paths_main_settings):
            setattr(self, string_model_field, self._path_project_model_folder / 
                    self.model_fields[string_model_field].default / path_main_settings)
            

_current_project_paths: ProjectPaths | None = None
    
    
def get_project_settings() -> ProjectPaths:
    if _current_project_paths is None:
        raise TypeError
    return _current_project_paths
        
def setup_project_paths(path_project_data_folder: Path, path_project_model_folder: Path) -> None:
    global _current_project_paths
    _current_project_paths = ProjectPaths(path_project_data_folder, path_project_model_folder)