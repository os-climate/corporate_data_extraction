import shutil
from pathlib import Path

import pytest
from train_on_pdf import link_extracted_files, link_files


@pytest.fixture(autouse=True)
def path_folders_required_linking(path_folder_temporary: Path) -> None:
    """Defines a fixture for creating the source, source_pdf and destination folder

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :return: None
    """
    path_folder_source = path_folder_temporary / "source"
    path_folder_source_pdf = path_folder_temporary / "source_pdf"
    path_folder_destination = path_folder_temporary / "destination"
    path_folder_source.mkdir(parents=True)
    path_folder_source_pdf.mkdir(parents=True)
    path_folder_destination.mkdir(parents=True)
    yield

    # cleanup
    for path in path_folder_temporary.glob("*"):
        shutil.rmtree(path)


def test_link_files(path_folder_temporary: Path):
    """Tests if link_files creates proper hard links
    Requesting path_folders_required_linking automatically (autouse)

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    path_folder_source = path_folder_temporary / "source"
    path_folder_source_pdf = path_folder_temporary / "source_pdf"
    path_folder_destination = path_folder_temporary / "destination"

    for i in range(10):
        path_current_file = path_folder_source / f"test_{i}.txt"
        path_current_file.touch()

    link_files(str(path_folder_source), str(path_folder_destination))

    for i in range(10):
        path_current_file = path_folder_source / f"test_{i}.txt"
        assert path_current_file.stat().st_nlink == 2


def test_link_extracted_files_result(path_folder_temporary: Path):
    """Tests if link_extracted_files returns True if executed
    Requesting path_folders_required_linking automatically (autouse)

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    path_folder_source = path_folder_temporary / "source"
    path_folder_source_pdf = path_folder_temporary / "source_pdf"
    path_folder_destination = path_folder_temporary / "destination"

    path_folder_source_file_pdf = path_folder_source / f"test.pdf"
    path_folder_source_file_json = path_folder_source / f"test.json"
    path_source_file_pdf = path_folder_source_pdf / f"test.pdf"

    result = link_extracted_files(str(path_folder_source), str(path_folder_source_pdf), str(path_folder_destination))
    assert result == True


def test_link_extracted_files_copy(path_folder_temporary: Path):
    """Tests if the extracted json files in folder_source has a regarding pdf in the folder_source_pdf
    and if so, copy the json file to the folder_destination
    Requesting path_folders_required_linking automatically (autouse)

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    path_folder_source = path_folder_temporary / "source"
    path_folder_source_pdf = path_folder_temporary / "source_pdf"
    path_folder_destination = path_folder_temporary / "destination"

    for i in range(10):
        path_current_file = path_folder_source / f"test_{i}.pdf"
        path_current_file.touch()
        path_current_file = path_folder_source / f"test_{i}.json"
        path_current_file.touch()
        path_current_file = path_folder_source_pdf / f"test_{i}.pdf"
        path_current_file.touch()

    for i in range(10):
        path_current_file = path_folder_destination / f"test_{i}.json"
        assert not path_current_file.exists() == True

    link_extracted_files(str(path_folder_source), str(path_folder_source_pdf), str(path_folder_destination))

    for i in range(10):
        path_current_file = path_folder_destination / f"test_{i}.json"
        assert path_current_file.exists() == True
