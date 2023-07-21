from pathlib import Path
from train_on_pdf import link_files, link_extracted_files
import shutil
import pytest


@pytest.fixture
def path_folders_required_linking(path_folder_temporary: Path) -> tuple[Path, Path, Path]:
    """Defines a fixture for creating the source, source_pdf and destination folder

    :param path_folder_temporary: Requesting the temporary folder fixture
    :type path_folder_temporary: Path
    :return: Tuple containing the paths to the source, source_pdf and destination folders
    :rtype: tuple[Path, Path, Path]
    :yield: Tuple containing the paths to the source, source_pdf and destination folders
    :rtype: Iterator[tuple[Path, Path, Path]]
    """
    path_folder_source = path_folder_temporary / 'source'
    path_folder_source_pdf = path_folder_temporary / 'source_pdf'
    path_folder_destination = path_folder_temporary / 'destination'
    path_folder_source.mkdir(parents = True)
    path_folder_source_pdf.mkdir(parents = True)
    path_folder_destination.mkdir(parents = True)
    yield (path_folder_source, path_folder_source_pdf, path_folder_destination)

    # cleanup
    for path in path_folder_temporary.glob("*"):
        shutil.rmtree(path)

def test_link_files(path_folders_required_linking: tuple[Path, Path, Path]):
    """Tests if link_files creates proper hard links

    :param path_folders_required_linking: Tuple containing the paths to the source
    source_pdf and destination folders
    :type path_folders_required_linking: tuple[Path, Path, Path]
    """
    path_folder_source, _, path_folder_destination = path_folders_required_linking
    
    # create sample files
    for i in range(10):
        path_current_file = path_folder_source / f'test_{i}.txt'
        path_current_file.touch()
    
    # perform the linking
    link_files(str(path_folder_source), str(path_folder_destination))
    
    # check for hard links
    for i in range(10):
        path_current_file = path_folder_source / f'test_{i}.txt'
        assert path_current_file.stat().st_nlink == 2


def test_link_extracted_files_result(path_folders_required_linking: tuple[Path, Path, Path]):
    """Tests if link_extracted_files returns True if executed

    :param path_folders_required_linking: Tuple containing the paths to the source
    source_pdf and destination folders
    :type path_folders_required_linking: tuple[Path, Path, Path]
    """
    path_folder_source, path_folder_source_pdf, path_folder_destination = path_folders_required_linking
    # single pdf and json file 
    path_folder_source_file_pdf = path_folder_source / f'test.pdf'
    path_folder_source_file_json = path_folder_source / f'test.json'
    path_source_file_pdf = path_folder_source_pdf / f'test.pdf'
    
    result = link_extracted_files(str(path_folder_source), str(path_folder_source_pdf),
                                  str(path_folder_destination))
    assert result == True
    
    
def test_link_extracted_files_copy(path_folders_required_linking: tuple[Path, Path, Path]):
    """Tests if the extracted json files in folder_source has a regarding pdf in the folder_source_pdf 
    and if so, copy the json file to the folder_destination

    :param path_folders_required_linking: Tuple containing the paths to the source
    source_pdf and destination folders
    :type path_folders_required_linking: tuple[Path, Path, Path]
    """
    path_folder_source, path_folder_source_pdf, path_folder_destination = path_folders_required_linking
    
    # create test pdf and json files in the source_extraction and source_pdf folders
    for i in range(10):
        path_current_file = path_folder_source / f'test_{i}.pdf'
        path_current_file.touch()
        path_current_file = path_folder_source / f'test_{i}.json'
        path_current_file.touch()
        path_current_file = path_folder_source_pdf / f'test_{i}.pdf'
        path_current_file.touch()
        
    # check if no files exist in the destination_extraction folder
    for i in range(10):
        path_current_file = path_folder_destination / f'test_{i}.json'
        assert not path_current_file.exists() == True
    
    # perform extracted file linking
    link_extracted_files(str(path_folder_source), str(path_folder_source_pdf),
                                  str(path_folder_destination))
    
    # check if files exist in the destination_extraction folder
    for i in range(10):
        path_current_file = path_folder_destination / f'test_{i}.json'
        assert path_current_file.exists() == True
