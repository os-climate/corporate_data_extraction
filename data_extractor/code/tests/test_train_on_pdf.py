from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock
import shutil
import train_on_pdf
import requests
import requests_mock
import typing
import config_path
import typing
from tests.test_utils.test_running import prerequisite_running


@pytest.fixture
def prerequisite_train_on_pdf_settings_files(path_folder_root_testing) -> tuple[Path, Path]:
    
    mocked_project_settings = {
        's3_usage': False,
        's3_settings': {},
        'general': 
            {
            'ext_port': 0,
            'infer_port': 0,
            'ext_ip': '0.0.0.0',
            'infer_ip': '0.0.0.0',
            'delete_interim_files': False
            },
        'train_relevance': 
            {
                'output_model_name': 'test',
                'train': False
            },
        'train_kpi':
            {
                'output_model_name': 'test',
                'train': False
            },
        'extraction':
            {
                'use_extractions': False,
                'store_extractions': False
            }
    }
    
    mocked_s3_settings = {
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
    
    yield mocked_project_settings, mocked_s3_settings
    
@pytest.fixture(params=(False, False))
def prerequisite_train_on_pdf_try_run(
    request,
    prerequisite_train_on_pdf_settings_files: tuple[Path, Path],
    path_folder_root_testing
    ) -> Mock:
    
    path_folder_data = path_folder_root_testing / 'data'
    path_folder_models = path_folder_root_testing / 'models'
    project_name = 'TEST'
    
    mocked_project_settings, _ = prerequisite_train_on_pdf_settings_files
    train_relevance, train_kpi = request.param
    mocked_project_settings['train_relevance']['train'] = train_relevance
    mocked_project_settings['train_kpi']['train'] = train_kpi

    with (
        patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,    
        patch('train_on_pdf.config_path', Mock()) as mocked_config_path,
        patch('train_on_pdf.yaml', Mock()) as mocked_yaml,
        patch('train_on_pdf.create_directory', Mock()) as mocked_create_directory
    ):
        mocked_argpase.return_value.project_name = project_name
        mocked_argpase.return_value.s3_usage = 'N'
        mocked_config_path.DATA_DIR = str(path_folder_data)
        mocked_config_path.MODEL_DIR = str(path_folder_models)
        mocked_yaml.safe_load.side_effect = lambda args: mocked_project_settings
        yield mocked_create_directory

def return_first_argument(*args, **kwargs):
    return args[0]
    
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


def test_train_on_pdf_s3_usage(prerequisite_train_on_pdf_settings_files):
    _, mocked_s3_settings = prerequisite_train_on_pdf_settings_files
    
    project_name = 'TEST'
    mock_s3_communication = Mock()
    mocked_open = MagicMock()
    mocked_yaml = Mock()
    
    try:
        with (
            patch('train_on_pdf.os.getenv', Mock(side_effect=return_first_argument)),
            patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
            patch('train_on_pdf.yaml', mocked_yaml),
            patch('train_on_pdf.open', mocked_open),
            patch('train_on_pdf.S3Communication', mock_s3_communication)
            ):
            mocked_argpase.return_value.project_name = project_name
            mocked_argpase.return_value.s3_usage = 'Y'
            mocked_yaml.safe_load.side_effect = lambda args: mocked_s3_settings
            
            train_on_pdf.main()

    except:
        pass
    finally:
        mocked_open.assert_any_call(f"{config_path.DATA_DIR}/s3_settings.yaml", "r")

        mock_s3_communication.assert_any_call(
            s3_endpoint_url=mocked_s3_settings['main_bucket']['s3_endpoint'],
            aws_access_key_id=mocked_s3_settings['main_bucket']['s3_access_key'],
            aws_secret_access_key=mocked_s3_settings['main_bucket']['s3_secret_key'],
            s3_bucket=mocked_s3_settings['main_bucket']['s3_bucket_name']
        )
        
        mock_s3_communication.assert_any_call(
            s3_endpoint_url=mocked_s3_settings['interim_bucket']['s3_endpoint'],
            aws_access_key_id=mocked_s3_settings['interim_bucket']['s3_access_key'],
            aws_secret_access_key=mocked_s3_settings['interim_bucket']['s3_secret_key'],
            s3_bucket=mocked_s3_settings['interim_bucket']['s3_bucket_name']
        )
        
        mock_s3_communication.return_value.download_file_from_s3.assert_called_once()


def test_train_on_pdf_required_settings_file(
    prerequisite_train_on_pdf_settings_files: tuple[Path, Path],
    path_folder_root_testing: Path,
    prerequisite_running):
    project_settings_expected, _ = prerequisite_train_on_pdf_settings_files
    
    try:
        with (
            patch('train_on_pdf.yaml', Mock()) as mocked_yaml,
            patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
        ):
            
            mocked_argpase.return_value.project_name = 'TEST'
            mocked_argpase.return_value.s3_usage = 'N'
            mocked_yaml.safe_load.side_effect = lambda args: project_settings_expected
        
            train_on_pdf.main()
    except:
        pytest.fail()

@pytest.mark.parametrize(
    'prerequisite_train_on_pdf_try_run', 
    [(True, False)], 
    indirect=True
) 
def test_train_on_pdf_folders_default_created(
    prerequisite_train_on_pdf_try_run: Mock,
    path_folder_root_testing
    ):
    
    mocked_create_directory = prerequisite_train_on_pdf_try_run
    paths_folders_default = [
        r'/interim/ml',
        r'/interim/pdfs/',
        r'/interim/ml/annotations/',
        r'/interim/kpi_mapping/',
        r'/interim/ml/extraction/',
        r'/interim/ml/training/',
        r'/interim/ml/curation/',
        r'/output/RELEVANCE/Text'
        ]
    
    with (
        patch('train_on_pdf.link_files', Mock()),
        patch('train_on_pdf.run_router', side_effect=lambda *args: False)
        ):
        train_on_pdf.main()
        
        path_folder_root_testing = path_folder_root_testing / 'data'
        path_folder_root_testing = str(path_folder_root_testing) + '/TEST'
        
        for path_current in paths_folders_default:
            path_folder_current = path_folder_root_testing + path_current
            mocked_create_directory.assert_any_call(str(path_folder_current))
    

@pytest.mark.parametrize(
    'prerequisite_train_on_pdf_try_run', 
    [(False, True)], 
    indirect=True
) 
@pytest.mark.parametrize(
    'paths_expected',
    [
        r'/RELEVANCE/Text/test',
        r'/KPI_EXTRACTION/Text/test'
    ]
    )
def test_train_on_pdf_folders_default_created(
    paths_expected,
    prerequisite_train_on_pdf_try_run: Mock,
    path_folder_root_testing
    ):
    
    mocked_create_directory = prerequisite_train_on_pdf_try_run
    
    with (
        patch('train_on_pdf.link_files', Mock()),
        patch('train_on_pdf.run_router', side_effect=lambda *args: False)
        ):
        train_on_pdf.main()
        
        path_folder_root_testing = path_folder_root_testing / 'models'
        path_folder_root_testing = str(path_folder_root_testing) + '/TEST'
        
        for path_current in paths_expected:
            path_folder_current = path_folder_root_testing + path_current
            mocked_create_directory.assert_any_call(str(path_folder_current))  