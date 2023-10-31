from pathlib import Path
from utils.helpers import create_tmp_file_path
from pydantic import Field
from pydantic_settings import BaseSettings
from utils.settings import Settings, MainSettings

path_file_running = create_tmp_file_path()


class ProjectPaths(BaseSettings):        
    _path_project_data_folder: Path
    _path_project_model_folder: Path
    
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

    def _check_for_project_data_folder_existence(self):
        pass
    
    @property
    def path_project_data_folder(self) -> Path:
        return self._path_project_data_folder
    
    @path_project_data_folder.setter
    def path_project_data_folder(self, path_new_project_data_folder: Path) -> None:
        list_all_paths_in_model: list[str] = list(self.model_fields.keys())

        for path_field in list_all_paths_in_model:
            if 'saved_models' not in path_field:
                path_field_default: Path = self.model_fields[path_field].default
                setattr(self, f'{path_field}', path_new_project_data_folder / path_field_default)
    
    @property
    def path_project_model_folder(self) -> Path:
        return self._path_project_model_folder
    
    @path_project_model_folder.setter
    def path_project_model_folder(self, Path_new_project_model_folder) -> None:
        list_all_paths_in_model: list[str] = list(self.model_fields.keys())

        for path_field in list_all_paths_in_model:
            if 'saved_models' in path_field:
                path_field_default: Path = self.model_fields[path_field].default
                setattr(self, f'{path_field}', Path_new_project_model_folder / path_field_default)


    
    
    # destination_saved_models_relevance = project_model_dir + r'/RELEVANCE/Text'  + r'/' + relevance_training_output_model_name
    # destination_saved_models_inference = project_model_dir + r'/KPI_EXTRACTION/Text' + r'/' + kpi_inference_training_output_model_name