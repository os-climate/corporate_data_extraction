from pathlib import Path
from train_on_pdf import save_train_info
import pytest
from unittest.mock import patch
import shutil
import train_on_pdf
import pickle

@pytest.fixture
def prerequisites_save_train_info(path_folder_root_testing: Path,
                                  path_folder_temporary: Path) -> Path:
    """Defines a fixture for creating all prerequisites for save_train_info

    :param path_folder_root_testing: Requesting the root testing folder fixture
    :type path_folder_root_testing: Path
    :param path_folder_temporary: Requesting the temporary folder fixture
    :type path_folder_temporary: Path
    :return: Returns path to pickled save_train_info file
    :rtype: Path
    :yield: Returns path to pickled save_train_info file
    :rtype: Iterator[Path]
    """
    # create sample project_settings
    mock_project_settings = {
        'train_relevance': {
            'output_model_name': 'TEST'
            },
        'train_kpi':{
            'output_model_name': 'TEST'
        }
    }
    # define required paths
    path_source_pdf = path_folder_root_testing / 'input' / 'pdf' / 'training'
    path_source_annotation = path_folder_root_testing / 'input' / 'pdfs' / 'training'
    path_source_mapping = path_folder_root_testing / 'data' / 'TEST' / 'input' / 'kpi_mapping'
    path_project_model_dir = path_folder_temporary / 'models'
    path_project_model_dir.mkdir(parents=True)
    # create path to save info pickle file
    relevance_model = mock_project_settings['train_relevance']['output_model_name']
    kpi_model = mock_project_settings['train_kpi']['output_model_name']
    file_train_info = f'rel_text_{relevance_model}_kpi_text_{kpi_model}.pickle'
    path_train_info = path_project_model_dir / file_train_info

    
    with (patch('train_on_pdf.project_settings', mock_project_settings),
          patch('train_on_pdf.source_annotation', str(path_source_annotation)),
          patch('train_on_pdf.source_mapping', str(path_source_mapping))):
        train_on_pdf.project_model_dir = str(path_project_model_dir)
        yield path_train_info
        
        # cleanup
        shutil.rmtree(path_folder_temporary)
        del train_on_pdf.project_model_dir


def test_save_train_info_pickle(prerequisites_save_train_info: Path):
    """Tests if the train info is pickle correctly

    :param prerequisites_save_train_info: Requesting the prerequisites_save_train_info fixture
    :type prerequisites_save_train_info: Path
    """
    project_name = 'TEST'
    
    path_train_info = prerequisites_save_train_info
    
    # perform the save_train_info call
    save_train_info(project_name)
    
    # check that a single pickle file exists
    assert path_train_info.exists()
    

def test_save_train_info_entries(prerequisites_save_train_info: Path):
    """Tests if all the train infos exists in the pickled train info file

    :param prerequisites_save_train_info: Requesting the prerequisites_save_train_info fixture
    :type prerequisites_save_train_info: Path
    """
    project_name = 'TEST'
    path_train_info = prerequisites_save_train_info
    
    # perform the save_train_info call
    save_train_info(project_name)
    
    # load pickled file
    with open(str(path_train_info), 'rb') as file:
        train_info = pickle.load(file)
    
    # define all expected keys
    required_keys = [
        'project_name',
        'train_settings',
        'pdfs_used',
        'annotations',
        'kpis'
    ]
    # check that all keys exist in dict
    assert all(key in required_keys for key in train_info.keys())
    

def test_save_tain_info_return_value(prerequisites_save_train_info: Path):
    project_name = 'TEST'
    path_train_info = prerequisites_save_train_info
    
    # perform and check for return value of save_train_info call
    assert save_train_info(project_name) is None
