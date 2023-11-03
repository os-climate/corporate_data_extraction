import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from utils.paths import ProjectPaths
from utils.settings import Settings, MainSettings


@pytest.fixture
def paths_project(main_settings: Settings) -> ProjectPaths:
    return ProjectPaths(path_project_data_folder=Path('/project_data_folder'),
                        path_project_model_folder=Path('/project_model_folder'),
                        main_settings=main_settings)


def test_check_that_all_required_paths_exist_in_project_path_object(main_settings: Settings):
    list_paths_expected = ['input/pdfs/training', 'input/annotations', 'input/kpi_mapping', 'interim/pdfs', 
                           'interim/ml/annotations', 'interim/kpi_mapping', 'interim/ml/extraction', 
                           'interim/ml/curation', 'interim/ml/training', 'RELEVANCE/Text', 'KPI_EXTRACTION/Text', 
                           'interim/ml', 'output/RELEVANCE/Text']

    with (patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_data_folder'),
          patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_model_folder')):
        paths_project: ProjectPaths = ProjectPaths(Path('/data'), Path('/model'), main_settings)
    
        for path_field in paths_project.model_fields.keys():
            path_field_attribute: Path = getattr(paths_project, f'{path_field}')
            assert str(path_field_attribute) in list_paths_expected


def test_project_paths_update_methods_are_called(main_settings: Settings):
    
    with (patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_data_folder') as mocked_update_data,
          patch.object(ProjectPaths, '_update_all_paths_depending_on_path_project_model_folder') as mocked_update_model):
        paths_project: ProjectPaths = ProjectPaths(Path('/data'), Path('/model'), main_settings)

    mocked_update_data.assert_called_once()
    mocked_update_model.assert_called_once()


def test_set_path_project_data_folder(paths_project: ProjectPaths):
    path_test_folder = Path('/data_folder')
    paths_project.path_project_data_folder: Path = path_test_folder
    assert paths_project.path_project_data_folder == path_test_folder


def test_set_path_project_model_folder(paths_project: ProjectPaths):
    path_test_folder = Path('/model_folder')
    paths_project.path_project_model_folder: Path = path_test_folder
    assert paths_project.path_project_model_folder == path_test_folder


def test_setting_path_project_model_folder_results_in_call_of_update_method(paths_project: ProjectPaths):
    path_test_folder: Path = Path('/model_folder_new')
    
    with patch.object(paths_project, '_update_all_paths_depending_on_path_project_model_folder') as mocked_method:
        paths_project.path_project_model_folder = path_test_folder
    
    mocked_method.assert_called_once()


def test_set_main_settings(paths_project: ProjectPaths, main_settings: Settings):
    main_settings_changed: MainSettings = MainSettings()
    main_settings_changed.general.project_name = 'TEST_NEW'

    paths_project.main_settings = main_settings_changed
    assert paths_project.main_settings != main_settings


def test_setting_main_settings_results_in_call_of_update_method(paths_project: ProjectPaths):
    main_settings_changed: MainSettings = MainSettings()
    main_settings_changed.general.project_name = 'TEST_NEW'
    
    with patch.object(paths_project, '_update_all_paths_depending_on_path_project_model_folder') as mocked_method:
        paths_project.main_settings = main_settings_changed
    
    mocked_method.assert_called_once()


def test_update_all_paths_depending_on_path_project_data_folder(paths_project: ProjectPaths):
    path_test_folder = Path('/data_folder')
    paths_project._path_project_data_folder: Path = path_test_folder

    paths_project._update_all_paths_depending_on_path_project_data_folder()
    
    list_paths_model_fields_filtered = [path_model_field for path_model_field in paths_project.model_fields.keys() 
                                        if 'saved_models' not in path_model_field]
    
    for path_field in list_paths_model_fields_filtered:
        path_field: Path = getattr(paths_project, f'{path_field}')
        assert path_field.parts[1] == path_test_folder.name


def test_update_all_paths_depending_on_path_project_model_folder(paths_project: ProjectPaths):
    main_settings_changed: MainSettings = MainSettings()
    main_settings_changed.general.project_name = 'TEST_NEW'
    paths_project._main_settings = main_settings_changed
    path_test_folder: Path = Path('/model_folder_new')
    paths_project._path_project_model_folder: Path = path_test_folder

    paths_project._update_all_paths_depending_on_path_project_model_folder()

    list_paths_model_fields_filtered: list[str] = [path_model_field for path_model_field in 
                                                   paths_project.model_fields.keys() if 'saved_models' in path_model_field]
    list_paths_main_settings: list[Path] = [Path(paths_project.main_settings.train_relevance.output_model_name),
                                           Path(paths_project.main_settings.train_kpi.output_model_name)]
    for path_model_field, path_main_settings in zip(list_paths_model_fields_filtered, list_paths_main_settings):
        path_model_field: Path = getattr(paths_project, f'{path_model_field}')
        assert path_model_field.parts[1] == path_test_folder.name
        assert path_model_field.parts[-1] == path_main_settings.name
    