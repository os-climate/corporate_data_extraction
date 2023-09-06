from utils.settings_handler import SettingsHandler
from tests.utils_test import project_tests_root
import pytest
from unittest.mock import patch

@pytest.fixture()
def settings_handler():
    return SettingsHandler()

def test_read_settings_files(settings_handler: SettingsHandler):
    path_tests_root = project_tests_root()
    path_root = path_tests_root.parent.parent
    
    path_settings_main = path_root / 'data' / 'TEST' / 'settings.yaml'
    path_settings_s3 = path_root / 'data' / 's3_settings.yaml'
    
    with (patch('utils.settings_handler.yaml'),
          patch('utils.settings_handler.open') as mocked_open):
        
        settings_handler.read_settings()
        
        mocked_open.assert_any_call(path_settings_main=str(path_settings_main))
        
        
    