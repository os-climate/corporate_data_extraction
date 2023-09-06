from typing import Dict, Any
from pathlib import Path
import yaml

class SettingsHandler():
    """
    Class for reading and writing setting files
    """
    def __init__(self):
        self.settings_main: None | Dict[Any] = None
        self.settings_s3: None | Dict[Any] = None
    
    def read_settings(self,
                      path_settings_main=Path(__file__).parent.parent / 'data' / 'TEST' / 'settings.yaml',
                      path_settings_s3=Path(__file__).parent.parent / 'data' / 's3_settings.yaml'):

        try:
            with (open(str(path_settings_main)) as file_settings_main,
                  open(str(path_settings_s3)) as file_settings_3):
                
                self.settings_main = yaml.safe_load(file_settings_main)
                self.settings_s3 = yaml.safe_load(file_settings_s3)
        except:
            pass
    
    def write_settings(self):
        pass
    