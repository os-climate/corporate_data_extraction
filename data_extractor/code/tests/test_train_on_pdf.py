from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
import shutil
import train_on_pdf
import requests
import requests_mock
import typing


def test_train_on_pdf_check_running(capsys):
    with patch('train_on_pdf.check_running') as mocked_function:
        return_value = train_on_pdf.main()
        
        output_cmd, _ = capsys.readouterr()
        
        string_expected = 'Another training or inference process is currently running.'
        train_on_pdf.check_running.assert_called_once()
        assert return_value is None
        assert string_expected in output_cmd


@pytest.mark.parametrize('project_name, output_expected',
                         [
                             (None,  None),
                             ("", None)
                         ]    
)
def test_train_on_pdf_wrong_inputs_given(project_name, 
                                         output_expected,
                                         capsys):
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', MagicMock()) as mocked_argpase,
          patch('builtins.input', MagicMock()) as mocked_input):
        mocked_argpase.return_value.project_name = project_name
        mocked_input.return_value = project_name
        return_value = train_on_pdf.main()
        
        output_cmd, _ = capsys.readouterr()
        
        string_expected = 'project name must not be empty'
        if project_name is None:
            string_call_expected = 'What is the project name? '
            mocked_input.assert_called_once()
        assert string_expected in output_cmd
        assert return_value is output_expected
            
def test_train_on_pdf_s3_usage():
    pass

def test_train_on_pdf_required_folders():
    pass

def test_train_on_pdf_required_folders_e2e():
    pass