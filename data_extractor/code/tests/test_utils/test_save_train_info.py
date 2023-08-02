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
    :return: Returns mocked project_model_dir
    :rtype: Path
    :yield: Returns mocked project_model_dir
    :rtype: Iterator[Path]
    """
    
    mock_project_settings = {
        'train_relevance': {
            'output_model_name': 'TEST'
            },
        'train_kpi':{
            'output_model_name': 'TEST'
        }
        }
    path_source_pdf = path_folder_root_testing / 'input' / 'pdf' / 'training'
    path_source_annotation = path_folder_root_testing / 'input' / 'pdfs' / 'training'
    path_source_mapping = path_folder_root_testing / 'data' / 'TEST' / 'input' / 'kpi_mapping'
    path_project_model_dir = path_folder_temporary / 'models'
    path_project_model_dir.mkdir(parents=True)

    
    with (patch('train_on_pdf.project_settings', mock_project_settings),
          patch('train_on_pdf.source_annotation', str(path_source_annotation)),
          patch('train_on_pdf.source_mapping', str(path_source_mapping))):
        train_on_pdf.project_model_dir = str(path_project_model_dir)
        yield path_project_model_dir
        
        # cleanup
        shutil.rmtree(path_folder_temporary)
        del train_on_pdf.project_model_dir


def test_save_train_info_pickle(prerequisites_save_train_info):
    """Tests if the train info is pickle correctly

    :param prerequisites_save_train_info: _description_
    :type prerequisites_save_train_info: _type_
    """
    project_name = 'TEST'
    
    path_project_model_dir = prerequisites_save_train_info
    
    save_train_info(project_name)
    
    assert len(list(path_project_model_dir.glob('*'))) == 1
    

def test_save_train_info_entries(prerequisites_save_train_info):
    
    project_name = 'TEST'
    
    path_project_model_dir = prerequisites_save_train_info
    
    save_train_info(project_name)
    
    path_pickled_train_info = list(path_project_model_dir.glob('*'))[0]
    
    with open(str(path_pickled_train_info), 'rb') as file:
        train_info = pickle.load(file)
    
    required_keys = [
        'project_name',
        'train_settings',
        'pdfs_used',
        'annotations',
        'kpis'
    ]
    
    assert required_keys in train_info.keys()
    

def test_save_tain_info_return_value(prerequisites_save_train_info):
    pass

