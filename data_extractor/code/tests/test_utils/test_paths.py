import pytest
from pathlib import Path
from utils.paths import ProjectPaths
from utils.settings import Settings


@pytest.fixture
def paths_project() -> ProjectPaths:
    return ProjectPaths()



def test_set_project_data_folder_and_update_all_paths(paths_project: ProjectPaths):
    path_project_folder: Path = Path('/test')

    paths_project.path_project_data_folder: Path = path_project_folder

    for path_field in paths_project.model_fields.keys():
        if 'saved_models' not in path_field:
            path_field: Path = getattr(paths_project, f'{path_field}')
            assert path_field.parts[1] == path_project_folder.name


def test_check_that_all_required_paths_exist_in_project_path_object(paths_project: ProjectPaths):
    list_paths_expected = ['input/pdfs/training', 'input/annotations', 'input/kpi_mapping', 'interim/pdfs', 
                           'interim/ml/annotations', 'interim/kpi_mapping', 'interim/ml/extraction', 
                           'interim/ml/curation', 'interim/ml/training', 'RELEVANCE/Text', 'KPI_EXTRACTION/Text', 
                           'interim/ml', 'output/RELEVANCE/Text']

    for path_field in paths_project.model_fields.keys():
        path_field_attribute: Path = getattr(paths_project, f'{path_field}')
        assert str(path_field_attribute) in list_paths_expected


def test_set_project_model_folder_and_update_paths(paths_project: ProjectPaths, main_settings: Settings):
    path_model_folder: Path = Path('/test')

    paths_project.path_project_model_folder: Path = path_model_folder

    for path_field in paths_project.model_fields.keys():
        if 'saved_models' in path_field:
            path_field_attribute: Path = getattr(paths_project, f'{path_field}')
            assert path_field_attribute.parts[1] == path_model_folder.name


            # destination_saved_models_relevance = project_model_dir + r'/RELEVANCE/Text'  + r'/' + relevance_training_output_model_name
    # destination_saved_models_inference = project_model_dir + r'/KPI_EXTRACTION/Text' + r'/' + kpi_inference_training_output_model_name