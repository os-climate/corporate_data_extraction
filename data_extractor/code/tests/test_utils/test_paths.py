import pytest
from pathlib import Path
from utils.paths import ProjectPaths


@pytest.fixture
def path() -> ProjectPaths:
    return ProjectPaths()

def test_set_project_data_folder_and_update_all_paths(path: ProjectPaths):
    string_path: str = '/test'
    path_project_folder: Path = Path(string_path)

    path.path_project_data_folder: Path = path_project_folder

    for path_field in path.model_fields.keys():
        if 'saved_models' not in path_field:
            path_field: Path = getattr(path, f'{path_field}')
            assert path_field.parts[1] == path_project_folder.name