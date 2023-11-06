from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock, call
import shutil
import train_on_pdf
import requests
import requests_mock
import config_path
import sys
import yaml
import traceback
from tests.utils_test import modify_project_settings
# from tests.test_utils.test_running import prerequisite_running

# types
import typing
from _pytest.fixtures import FixtureRequest
from _pytest.capture import CaptureFixture


@pytest.fixture(params=[()], autouse=True)
def prerequisite_train_on_pdf_try_run(
    request: FixtureRequest,
    path_folder_root_testing: Path,
    path_folder_temporary: Path
    ) -> None:
    """Defines a fixture for the train_on_pdf script

    :param request: Request for parametrization
    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
    :type path_folder_root_testing: Path
    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :param prerequisite_running: Requesting the prerequisite_running fixture
    :rtype prerequisite_train_on_pdf_try_run: None
    """
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
    project_name = 'TEST'
    path_folder_data = path_folder_temporary / 'data'
    path_folder_models = path_folder_temporary / 'models'
    Path(path_folder_data / project_name).mkdir(parents=True, exist_ok=True)
    path_folder_models.mkdir(parents=True, exist_ok=True)
    
    # copy settings files to temporary folder
    path_file_settings_root_testing = path_folder_root_testing / 'data' / project_name / 'settings.yaml'
    path_file_settings_temporary = path_folder_temporary / 'data' / project_name / 'settings.yaml'
    
    path_file_settings_s3_root_testing = path_folder_root_testing / 'data' / 's3_settings.yaml'
    path_file_settings_s3_temporary = path_folder_temporary / 'data' / 's3_settings.yaml'
    
    shutil.copy(path_file_settings_root_testing, path_file_settings_temporary)
    shutil.copy(path_file_settings_s3_root_testing, path_file_settings_s3_temporary)

    def return_project_settings(*args: typing.List[Mock]):
        """Helper function for choosing the right settings file

        :return: Project or S3 Settings file
        :rtype: typing.Dict[str]
        """
        if 's3' in args[0].name:
            return mocked_s3_settings
        else:
            return mocked_project_settings
    
    # modifying the project settings file via parametrization
    mocked_project_settings = modify_project_settings(mocked_project_settings, request.param)

    with (
        patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,    
        patch('train_on_pdf.config_path', Mock()) as mocked_config_path,
        patch('train_on_pdf.yaml', Mock()) as mocked_yaml,
        patch('train_on_pdf.project_settings', mocked_project_settings),
        patch('utils.training_monitor.TrainingMonitor', Mock()) as mocked_training_monitor
    ):
        mocked_argpase.return_value.project_name = project_name
        mocked_argpase.return_value.s3_usage = 'N'
        mocked_config_path.DATA_DIR = str(path_folder_data)
        mocked_config_path.MODEL_DIR = str(path_folder_models)
        mocked_yaml.safe_load.side_effect = return_project_settings
        mocked_training_monitor.check_running.return_value = False
        yield
        
        # cleanup
        shutil.rmtree(path_folder_temporary)

  
def test_train_on_pdf_check_running(capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests if everything is printed when another training is running

    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None])
    """
    with patch('train_on_pdf.TrainingMonitor', Mock()) as mocked_training_monitor:
        mocked_training_monitor.check_running.return_value = True
        return_value = train_on_pdf.main()
        
        output_cmd, _ = capsys.readouterr()
        string_expected = 'Another training or inference process is currently running.'
        mocked_training_monitor.return_value.check_running.assert_called_once()
        assert return_value is None
        assert string_expected in output_cmd


@pytest.mark.parametrize('project_name',
                         [None, 
                         ''])
def test_train_on_pdf_wrong_input_project_name(project_name: typing.Union[str, None],
                                               capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests the correct behaviour of wrong given project names

    :param project_name: Project name
    :type project_name: typing.Union[str, None]
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None])
    """
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
        assert return_value is None
        

def test_train_on_pdf_correct_input_project_name():
    """Tests that a correct project name is accepted
    """
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.input', Mock()) as mocked_input):
        mocked_argpase.return_value.s3_usage = True
        mocked_input.side_effect = lambda: 'TEST'
        
        train_on_pdf.main()
        
        assert mocked_input() == 'TEST'


@pytest.mark.parametrize('s3_usage',
                         [None, 
                          'X'])
def test_train_on_pdf_wrong_input_s3(s3_usage: typing.Union[str, None],
                                     capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests the correct behaviour of wrong s3 input is given

    :param s3_usage: S3 usage (yes or no)
    :type s3_usage: typing.Union[str, None]
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None])
    """
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
        assert return_value is None

            
@pytest.mark.parametrize('s3_usage',
                         ['Y', 
                          'N'])
def test_train_on_pdf_correct_input_s3_usage(s3_usage: typing.Union[str, None]):
    """Tests that the correct s3 usage is accepted

    :param s3_usage: S3 usage (yes or no)
    :type s3_usage: typing.Union[str, None]
    """
    with (patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.input', Mock()) as mocked_input,
          patch('train_on_pdf.create_folder', 
                side_effect=lambda *args: Path(args[0]).mkdir(parents=True, exist_ok=True)),
          patch('train_on_pdf.S3Communication', Mock()) as mocked_s3_communication):
        mocked_argpase.return_value.project_name = 'TEST'
        mocked_argpase.return_value.s3_usage = None
        mocked_input.side_effect = lambda *args: s3_usage
        
        train_on_pdf.main()
        
        assert mocked_input() == s3_usage
        if s3_usage == 'Y':
            assert mocked_s3_communication.call_count == 2
            
            mocked_s3_communication.return_value.download_file_from_s3.assert_called_once()


def test_train_on_pdf_s3_usage():
    """Tests if the s3 usage is correctly performed

    """
    project_name = 'TEST'

    with (patch('train_on_pdf.os.getenv', Mock(side_effect=lambda *args: args[0])),
          patch('train_on_pdf.argparse.ArgumentParser.parse_args', Mock()) as mocked_argpase,
          patch('train_on_pdf.S3Communication', Mock()) as mocked_s3_communication,
          patch('train_on_pdf.create_folder', Mock())):
        
        mocked_argpase.return_value.project_name = project_name
        mocked_argpase.return_value.s3_usage = 'Y'
        
        train_on_pdf.main()
        
        mocked_s3_communication.assert_any_call(
            s3_endpoint_url='S3_END_MAIN',
            aws_access_key_id='S3_ACCESS_MAIN',
            aws_secret_access_key='S3_SECRET_MAIN',
            s3_bucket='S3_NAME_MAIN'
        )
        
        mocked_s3_communication.assert_any_call(
            s3_endpoint_url='S3_END_INTERIM',
            aws_access_key_id='S3_ACCESS_INTERIM',
            aws_secret_access_key='S3_SECRET_INTERIM',
            s3_bucket='S3_NAME_INTERIM'
        )
        
        mocked_s3_communication.return_value.download_file_from_s3.assert_called_once()


def test_train_on_pdf_folders_default_created(path_folder_temporary: Path):
    """Tests of the required default folders are created

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    
    paths_folders_expected = [
        r'/interim/ml',
        r'/interim/pdfs/',
        r'/interim/ml/annotations/',
        r'/interim/kpi_mapping/',
        r'/interim/ml/extraction/',
        r'/interim/ml/training/',
        r'/interim/ml/curation/',
        r'/output/RELEVANCE/Text']
    
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=False)),
          patch('train_on_pdf.create_folder', Mock()) as mocked_create_folder):
        
        train_on_pdf.main()
        
        # we have to combine pathlib object with str path...
        path_folder_temporary = path_folder_temporary / 'data'
        path_folder_temporary = str(path_folder_temporary) + '/TEST'
        for path_current in paths_folders_expected:
            path_folder_current = path_folder_temporary + path_current
            mocked_create_folder.assert_any_call(Path(path_folder_current))
    

@pytest.mark.parametrize('prerequisite_train_on_pdf_try_run', 
                         [('train_relevance', 'train', True)], 
                         indirect=True) 
def test_train_on_pdf_folders_relevance_created(path_folder_temporary: Path):
    """Tests of the relevance folder is created

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=False)),
          patch('train_on_pdf.create_folder', Mock()) as mocked_create_folder):
        
        train_on_pdf.main()
        
        # we have to combine pathlib object with str path...
        path_folder_temporary = path_folder_temporary / 'models'
        path_folder_temporary = str(path_folder_temporary) + '/TEST'
        path_folder_expected = path_folder_temporary + '/RELEVANCE/Text/test'
        mocked_create_folder.assert_any_call(Path(path_folder_expected))

            
@pytest.mark.parametrize('prerequisite_train_on_pdf_try_run', 
                         [('train_kpi', 'train', True)], 
                         indirect=True) 
def test_train_on_pdf_folders_kpi_extraction_created(path_folder_temporary: Path):
    """Tests of the kpi extraction folder is created

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    """
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=False)),
          patch('train_on_pdf.create_folder', Mock()) as mocked_create_folder):
        
        train_on_pdf.main()
        
        # we have to combine pathlib object with str path...
        path_folder_temporary = path_folder_temporary / 'models'
        path_folder_temporary = str(path_folder_temporary) + '/TEST'
        path_folder_expected = path_folder_temporary + '/KPI_EXTRACTION/Text/test'
        mocked_create_folder.assert_any_call(Path(path_folder_expected))
                  

@pytest.mark.parametrize('prerequisite_train_on_pdf_try_run', 
                         [('extraction', 'store_extractions', True)], 
                         indirect=True) 
def test_train_on_pdf_e2e_store_extractions(path_folder_temporary: Path,
                                            capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests of the extraction works properly

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None])
    """
    
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=True)),
          patch('train_on_pdf.XlsToCsvConverter'),
          patch('train_on_pdf.save_train_info', Mock()) as mocked_save_train_info,
          patch('train_on_pdf.copy_file_without_overwrite', Mock()) as mocked_copy_files,
          patch('train_on_pdf.create_folder', Mock())):
        mocked_copy_files.return_value = False
        
        train_on_pdf.main()
        
        # we have to combine pathlib object with str path...
        path_folder_root = path_folder_temporary / 'data'
        path_folder_root_source = str(path_folder_root) + '/TEST/interim/ml/extraction'
        path_folder_root_destination = str(path_folder_root) + '/TEST/output/TEXT_EXTRACTION'
        output_cmd, _ = capsys.readouterr()
        
        assert 'Finally we transfer the text extraction to the output folder\n' in output_cmd
        mocked_copy_files.assert_called_with(path_folder_root_source, path_folder_root_destination)


@pytest.mark.parametrize('prerequisite_train_on_pdf_try_run', 
                         [('general', 'delete_interim_files', True)], 
                         indirect=True) 
def test_train_on_pdf_e2e_delete_interim_files(path_folder_temporary: Path):
    """Tests if interim files are getting deleted

    :param path_folder_root_testing: Requesting the path_folder_root_testing fixture
    :type path_folder_root_testing: Path
    """
    
    # define the folders for getting checked
    paths_folders_expected = [
        r'interim/pdfs/',
        r'interim/kpi_mapping/',
        r'interim/ml/annotations/',
        r'interim/ml/extraction/',
        r'interim/ml/training/',
        r'interim/ml/curation/',
        ]
    
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=True)),
          patch('train_on_pdf.XlsToCsvConverter'),
          patch('train_on_pdf.save_train_info', Mock()),
          patch('train_on_pdf.create_folder', Mock()) as mocked_create_folder):
        
        train_on_pdf.main()
        
        # we have to combine pathlib object with str path...
        path_folder_temporary = path_folder_temporary / 'data' / 'TEST'
        for path_current in paths_folders_expected:
            path_folder_current = path_folder_temporary / path_current
            # we have to check for two calls since create_folder deletes the current folder if it exists...
            mocked_create_folder.assert_has_calls([call(path_folder_current), call(path_folder_current)], any_order=True)


def test_train_on_pdf_e2e_save_train_info(capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests if the train info of this run is saved

    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None]
    """
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=True)),
          patch('train_on_pdf.XlsToCsvConverter'),
          patch('train_on_pdf.save_train_info', Mock()) as mocked_save_train_info,
          patch('train_on_pdf.create_folder', Mock())): 
        train_on_pdf.main()
        
        mocked_save_train_info.assert_called_once()
        output_cmd, _ = capsys.readouterr()
        assert output_cmd == "End-to-end inference complete\n"

        
def test_train_on_pdf_process_failed(capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests for cmd output if exception is raised

    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None]
    """
    with (patch('train_on_pdf.link_files', Mock()),
          patch('train_on_pdf.Router', Mock(run_router=False)),
          patch('train_on_pdf.link_files', side_effect=ValueError()),
          patch('train_on_pdf.create_folder', lambda *args: Path(args[0]).mkdir(exist_ok=True))):
        
        train_on_pdf.main()
        
        output_cmd, _ = capsys.readouterr()
        assert "Process failed to run. Reason: " in output_cmd


def test_train_on_pdf_download_from_s3_if_required():

    with (patch('train_on_pdf.link_files'),
          patch('train_on_pdf.Router', Mock(run_router=False)),
          patch('train_on_pdf.XlsToCsvConverter'),
          patch('train_on_pdf.create_folder'),
          patch('train_on_pdf.download_data_from_s3_main_bucket_to_local_folder_if_required') as mocked_download,
          patch('train_on_pdf.upload_data_from_local_folder_to_s3_interim_bucket_if_required')): 
        train_on_pdf.main() 
    

    mocked_download.assert_called_once()


def test_train_on_pdf_upload_to_s3_if_required():
    
    with (patch('train_on_pdf.link_files'),
          patch('train_on_pdf.Router', Mock(run_router=False)),
          patch('train_on_pdf.XlsToCsvConverter'),
          patch('train_on_pdf.create_folder'),
          patch('train_on_pdf.download_data_from_s3_main_bucket_to_local_folder_if_required'),
          patch('train_on_pdf.upload_data_from_local_folder_to_s3_interim_bucket_if_required') as mocked_upload): 
        train_on_pdf.main() 
    

    mocked_upload.assert_called_once()