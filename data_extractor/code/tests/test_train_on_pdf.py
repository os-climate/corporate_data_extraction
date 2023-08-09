from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock
import shutil
import train_on_pdf
import requests
import requests_mock
import typing
import config_path


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
                             ('', None)
                         ]    
)
def test_train_on_pdf_wrong_input_project_name(project_name,
                                               output_expected,
                                               capsys):
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.input', Mock()) as mocked_input):
        mocked_argpase.return_value.project_name = project_name
        mocked_input.return_value = project_name
        return_value = train_on_pdf.main()
        
        output_cmd, _ = capsys.readouterr()
        
        string_expected = 'project name must not be empty'
        if project_name is None:
            string_call_expected = 'What is the project name? '
            mocked_input.assert_called_once()
            mocked_input.assert_called_with(string_call_expected) 
        assert string_expected in output_cmd
        assert return_value is output_expected
            
def test_train_on_pdf_correct_input_project_name():
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.input', Mock()) as mocked_input):
        mocked_argpase.return_value.s3_usage = True
        mocked_input.side_effect = lambda: 'TEST'
        
        train_on_pdf.main()
        assert mocked_input() == 'TEST'

@pytest.mark.parametrize('s3_usage, output_expected',
                         [
                             (None, None),
                             ('X', None)
                         ])
def test_train_on_pdf_wrong_input_s3(s3_usage, 
                                     output_expected,
                                     capsys):
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.input', Mock()) as mocked_input):
        mocked_argpase.return_value.project_name = 'TEST'
        mocked_argpase.return_value.s3_usage = s3_usage
        return_value = train_on_pdf.main()
        
        output_cmd, _ = capsys.readouterr()
        
        string_expected = 'Answer to S3 usage must by Y or N. Stop program. Please restart.'
        if s3_usage is None:
            string_call_expected = 'Do you want to use S3? Type either Y or N.'
            mocked_input.assert_called_once()
            mocked_input.assert_called_with(string_call_expected)
        assert string_expected in output_cmd
        assert return_value is output_expected
            
@pytest.mark.parametrize('s3_usage',
                         ['Y', 'N'])
def test_train_on_pdf_correct_input_s3_usage(s3_usage):
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.input', Mock()) as mocked_input):
        mocked_argpase.return_value.project_name = 'TEST'
        mocked_input.side_effect = lambda: s3_usage
        
        train_on_pdf.main()
        assert mocked_input() == s3_usage


def return_args(*args, **kwargs):
    def inner_return(*args, **kwargs):
        return args[0]
    return inner_return(*args, **kwargs)

def test_train_on_pdf_s3_usage():
    mock_s3_settings = {
        'prefix': 'test_prefix',
        'main_bucket': {
            's3_endpoint': 'S3_END_MAIN',
            's3_access_key': 'S3_ACCESS_MAIN',
            's3_secret_key': 'S3_SECRET_MAIN',
            's3_bucket_name': 'S3_NAME_MAIN'
        },
        'interim_bucket': {
            's3_endpoint': 'S3_END_INTERIM',
            's3_access_key': 'S3_ACCESS_INTERIM',
            's3_secret_key': 'S3_SECRET_INTERIM',
            's3_bucket_name': 'S3_NAME_INTERIM'
        }
  
    }
    project_name = 'TEST'
    mock_s3_communication = Mock()
    mocked_open = MagicMock()
    mocked_yaml = Mock()
    
    try:
        with (
            patch('train_on_pdf.os.getenv', Mock(side_effect=return_args)),
            patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
            patch('train_on_pdf.yaml', mocked_yaml),
            patch('train_on_pdf.open', mocked_open),
            patch('train_on_pdf.S3Communication', mock_s3_communication)
            ):
            mocked_argpase.return_value.project_name = project_name
            mocked_argpase.return_value.s3_usage = 'Y'
            mocked_yaml.safe_load.side_effect = lambda args: mock_s3_settings
            
            train_on_pdf.main()

    except:
        mocked_open.assert_any_call(f"{config_path.DATA_DIR}/s3_settings.yaml", "r")

        mock_s3_communication.assert_any_call(
            s3_endpoint_url=mock_s3_settings['main_bucket']['s3_endpoint'],
            aws_access_key_id=mock_s3_settings['main_bucket']['s3_access_key'],
            aws_secret_access_key=mock_s3_settings['main_bucket']['s3_secret_key'],
            s3_bucket=mock_s3_settings['main_bucket']['s3_bucket_name']
        )
        
        mock_s3_communication.assert_any_call(
            s3_endpoint_url=mock_s3_settings['interim_bucket']['s3_endpoint'],
            aws_access_key_id=mock_s3_settings['interim_bucket']['s3_access_key'],
            aws_secret_access_key=mock_s3_settings['interim_bucket']['s3_secret_key'],
            s3_bucket=mock_s3_settings['interim_bucket']['s3_bucket_name']
        )


def test_train_on_pdf_required_folders():
    pass

def test_train_on_pdf_required_folders_e2e():
    pass