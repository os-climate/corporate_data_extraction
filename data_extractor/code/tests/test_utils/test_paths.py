import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from utils.paths import ProjectPaths
from utils.settings import Settings, MainSettings


@pytest.fixture
def path_folder_config_path() -> Path:
    return Path(__file__).parents[3]


@pytest.fixture
def paths_project(main_settings: Settings) -> ProjectPaths:
    return ProjectPaths(string_project_name='test_project',
                        main_settings=main_settings)


def test_root_folder_set(path_folder_config_path: Path, 
                         paths_project: ProjectPaths):
    assert paths_project.PATH_FOLDER_ROOT == path_folder_config_path


def test_model_folder_set(path_folder_config_path: Path, 
                          paths_project: ProjectPaths):
    path_folder_model: Path = path_folder_config_path / 'models'
    assert paths_project.PATH_FOLDER_MODEL == path_folder_model


def test_data_folder_set(path_folder_config_path: Path,
                         paths_project: ProjectPaths):
    path_folder_data: Path = path_folder_config_path / 'data'
    assert paths_project.PATH_FOLDER_DATA == path_folder_data


def test_nlp_folder_set(path_folder_config_path: Path,
                        paths_project: ProjectPaths):
    assert paths_project.PATH_FOLDER_NLP == path_folder_config_path


def test_python_executable_set(paths_project: ProjectPaths):
    assert paths_project.PYTHON_EXECUTABLE == 'python'


def test_check_that_all_required_paths_exist_in_project_path_object(main_settings: Settings):
    list_paths_expected = ['input/pdfs/training', 'input/annotations', 'input/kpi_mapping', 'interim/pdfs', 
                           'interim/ml/annotations', 'interim/kpi_mapping', 'interim/ml/extraction', 
                           'interim/ml/curation', 'interim/ml/training', 'RELEVANCE/Text', 'KPI_EXTRACTION/Text', 
                           'interim/ml', 'output/RELEVANCE/Text']

    with (patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_data_folder'),
          patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_model_folder')):
        paths_project: ProjectPaths = ProjectPaths('new_test_project', main_settings)
    
        for path_field in paths_project.model_fields.keys():
            path_field_attribute: Path = getattr(paths_project, f'{path_field}')
            assert str(path_field_attribute) in list_paths_expected


def test_project_paths_update_methods_are_called(main_settings: Settings):
    
    with (patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_data_folder') as mocked_update_data,
          patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_model_folder') as mocked_update_model):
        paths_project: ProjectPaths = ProjectPaths('new_test_project', main_settings)

    mocked_update_data.assert_called_once()
    mocked_update_model.assert_called_once()


def test_set_path_project_data_folder(paths_project: ProjectPaths):
    string_test_project: str = 'test_project'
    paths_project.string_project_name: str = string_test_project
    assert paths_project.path_project_data_folder.parts[-1] == string_test_project


def test_set_path_project_model_folder(paths_project: ProjectPaths):
    string_test_project: str = 'test_project'
    paths_project.string_project_name: str = string_test_project
    assert paths_project.path_project_model_folder.parts[-1] == string_test_project


def test_setting_new_project_name_results_in_call_of_update_methods(paths_project: ProjectPaths):
    string_test_project: str = 'test_project'
    
    with (patch.object(paths_project, '_update_all_paths_depending_on_path_project_data_folder') as mocked_update_data,
          patch.object(paths_project, '_update_all_paths_depending_on_path_project_model_folder') as mocked_update_model):
        paths_project.string_project_name: str = string_test_project
    
    mocked_update_data.assert_called_once()
    mocked_update_model.assert_called_once()


def test_set_main_settings(paths_project: ProjectPaths, main_settings: Settings):
    main_settings_changed: MainSettings = MainSettings()
    main_settings_changed.general.project_name = 'TEST_NEW'

    paths_project.main_settings: MainSettings = main_settings_changed
    assert paths_project.main_settings != main_settings


def test_update_all_paths_depending_on_path_project_data_folder(paths_project: ProjectPaths):
    string_test_project: str = 'test_project'
    paths_project.string_project_name: str = string_test_project

    paths_project._update_all_paths_depending_on_path_project_data_folder()
    
    list_paths_model_fields_filtered = [path_model_field for path_model_field in paths_project.model_fields.keys() 
                                        if 'saved_models' not in path_model_field]
    
    for path_field in list_paths_model_fields_filtered:
        path_field: Path = getattr(paths_project, f'{path_field}')
        assert string_test_project in path_field.parts


def test_update_all_paths_depending_on_path_project_model_folder(paths_project: ProjectPaths):
    main_settings_changed: MainSettings = MainSettings()
    main_settings_changed.general.project_name = 'TEST_NEW'
    paths_project._main_settings: MainSettings = main_settings_changed
    string_test_project: str = 'test_project'
    paths_project.string_project_name: str = string_test_project

    paths_project._update_all_paths_depending_on_path_project_model_folder()

    list_paths_model_fields_filtered: list[str] = [path_model_field for path_model_field in 
                                                   paths_project.model_fields.keys() if 'saved_models' in path_model_field]
    list_paths_main_settings: list[Path] = [Path(paths_project.main_settings.train_relevance.output_model_name),
                                           Path(paths_project.main_settings.train_kpi.output_model_name)]
    for path_model_field, path_main_settings in zip(list_paths_model_fields_filtered, list_paths_main_settings):
        path_model_field: Path = getattr(paths_project, f'{path_model_field}')
        assert string_test_project in path_model_field.parts
        assert path_model_field.parts[-1] == path_main_settings.name

    