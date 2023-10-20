from pathlib import Path
# from utils.router import run_router
import pytest
from unittest.mock import patch, Mock
import train_on_pdf
import requests_mock
from tests.test_utils.test_generate_text import prerequisites_generate_text
from utils.s3_communication import S3Communication
from utils.settings import S3Settings, MainSettings
from utils.router import Router

# types
import typing
from _pytest.capture import CaptureFixture


@pytest.fixture
def router(main_settings: MainSettings, s3_settings: S3Settings):
    dict_general_settings = {'project_name': 'TEST',
                             'ext_ip': '0.0.0.0', 
                             'ext_port': '8000',
                             'infer_ip': '0.0.0.1', 
                             'infer_port': '8000'}
    mocked_general_settings = Mock(**dict_general_settings)

    with (patch.object(main_settings, 'general', mocked_general_settings)):
        yield Router(main_settings=main_settings, s3_settings=s3_settings, converter=Mock())

@pytest.fixture
def prerequisites_run_router(prerequisites_generate_text,
                             main_settings
                             ) -> requests_mock.mocker.Mocker:
    """Prerequisites for running the function run_router

    :param prerequisites_generate_text: Requesting fixture for running function generate_text (required in 
    run_router)
    :rtype: requests_mock.mocker.Mocker
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    dict_general_settings = {'project_name': 'TEST',
                             'ext_ip': extraction_ip, 
                             'ext_port': extraction_port,
                             'infer_ip': inference_ip, 
                             'infer_port': inference_port}
    mocked_general_settings = Mock(**dict_general_settings)

    with (requests_mock.Mocker() as mocked_server,
          patch.object(main_settings, 'general', mocked_general_settings),
          patch('train_on_pdf.XlsToCsvConverter'),
          patch('train_on_pdf.json')):
        mocked_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
        mocked_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=200)
        mocked_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=200)
        mocked_server.get(f'http://{inference_ip}:{inference_port}/liveness', status_code=200)
        mocked_server.get(f'http://{inference_ip}:{inference_port}/train_relevance', status_code=200)
        mocked_server.get(f'http://{inference_ip}:{inference_port}/infer_relevance', status_code=200)
        mocked_server.get(f'http://{inference_ip}:{inference_port}/train_kpi', status_code=200)
        yield mocked_server
    

@pytest.mark.parametrize('status_code, cmd_output_expected, return_value_expected',
                         [
                             (200, 'Extraction server is up. Proceeding to extraction.', False),
                             (-1, 'Extraction server is not responding.', False)
                         ])
def test_run_router_extraction_liveness_up(prerequisites_run_router: requests_mock.mocker.Mocker,
                                           main_settings: MainSettings,
                                           s3_settings: S3Settings,
                                           status_code: int, 
                                           cmd_output_expected: str,
                                           return_value_expected: bool,
                                           capsys: typing.Generator[CaptureFixture[str], None, None],
                                           router: Router):
    """Tests the liveness of the extraction server

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    :param status_code: Status code used in extraction server
    :type status_code: int
    :param cmd_output_expected: Expeceted cmd output
    :type cmd_output_expected: str
    :param return_value_expected: Expected return_value
    :type return_value_expected: bool
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None])
    """    
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    mocked_server = prerequisites_run_router
    
    mocked_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=status_code)
    mocked_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=-1)
    return_value = router.run_router()

    cmd_output, _ = capsys.readouterr()
    assert cmd_output_expected in cmd_output
    assert return_value == return_value_expected


def test_run_router_extraction_server_down(prerequisites_run_router: requests_mock.mocker.Mocker,
                                           main_settings: MainSettings,
                                           s3_settings: S3Settings,
                                           router: Router):
    """Tests the return value if the extraction server is down

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    mocked_server = prerequisites_run_router
    
    mocked_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=-1)
    return_value = router.run_router()

    assert return_value is False


def test_run_router_extraction_curation_server_down(prerequisites_run_router: requests_mock.mocker.Mocker,
                                                    main_settings: MainSettings,
                                                    s3_settings: S3Settings,
                                                    router: Router):
    """Tests the return value of the curation of the extraction server

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    mocked_server = prerequisites_run_router
    
    mocked_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=-1)      
    return_value = router.run_router()

    assert return_value is False


@pytest.mark.parametrize('status_code, cmd_output_expected, return_value_expected',
                         [
                             (200, 'Inference server is up. Proceeding to Inference.', True),
                             (-1, 'Inference server is not responding.', False)
                         ])
def test_run_router_inference_liveness(prerequisites_run_router: requests_mock.mocker.Mocker,
                                       main_settings: MainSettings,
                                       s3_settings: S3Settings,
                                       status_code: int, 
                                       cmd_output_expected: str,
                                       return_value_expected: bool,
                                       capsys: typing.Generator[CaptureFixture[str], None, None],
                                       router: Router):
    """Tests the liveness of the inference server, up as well as down

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    :param status_code: Status code for liveness
    :type status_code: int
    :param cmd_output_expected: Expected cmd output
    :type cmd_output_expected: str
    :param return_value_expected: Expected return_value
    :type return_value_expected: bool
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None]
    """
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    mocked_server = prerequisites_run_router
    

    mocked_server.get(f'http://{inference_ip}:{inference_port}/liveness', status_code=status_code)
    return_value = router.run_router()
    
    cmd_output, _ = capsys.readouterr()
    assert cmd_output_expected in cmd_output
    assert return_value == return_value_expected


@pytest.mark.parametrize('train_relevance, status_code, cmd_output_expected, return_value_expected',
                         [
                            (True, -1, "Relevance training will be started.", False),
                            (True, 200, "Relevance training will be started.", True),
                            (False, -1, ("No relevance training done. If you want to have a relevance training please "
                                         "set variable train under train_relevance to true."), True)
                         ])
def test_run_router_relevance_training(prerequisites_run_router: requests_mock.mocker.Mocker,
                                       main_settings: MainSettings,
                                       s3_settings: S3Settings,
                                       train_relevance: bool, 
                                       status_code: int,
                                       cmd_output_expected: str,
                                       return_value_expected: bool, 
                                       capsys: typing.Generator[CaptureFixture[str], None, None],
                                       router: Router):
    """Tests if the relevance training fails and successfully starts

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    :param train_relevance: Flag for train relevance
    :type train_relevance: bool
    :param status_code: Status code for train relevance
    :type status_code: int
    :param cmd_output_expected: Expected cmd output
    :type cmd_output_expected: str
    :param return_value_expected: Expected return_value
    :type return_value_expected: bool
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None]
    """
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    mocked_server = prerequisites_run_router

    with patch.object(main_settings, 'train_relevance', Mock(train=train_relevance)):
        mocked_server.get(f'http://{inference_ip}:{inference_port}/train_relevance', status_code=status_code)
        return_value = router.run_router()

    cmd_output, _ = capsys.readouterr()
    assert cmd_output_expected in cmd_output
    assert return_value == return_value_expected


@pytest.mark.parametrize('train_kpi, status_code_infer_relevance, project_name, status_code_train_kpi, cmd_output_expected, return_value_expected',
                         [
                            (True, -1, "TEST", -1, "", False),
                            (True, 200, "TEST", -1, "text_3434 was generated without error", False),
                            (True, 200, "TEST", 200, "text_3434 was not generated without error", True),
                            (True, 200, None, -1, "Error while generating text_3434.", False),
                            (True, 200, None, 200, "Error while generating text_3434.", True),
                            (False, -1, None, -1, ("No kpi training done. If you want to have a kpi "
                                                    "training please set variable train under train_kpi to true."), True)
                         ])
def test_run_router_kpi_training(prerequisites_run_router: requests_mock.mocker.Mocker,
                                 main_settings: MainSettings,
                                 s3_settings: S3Settings,
                                 train_kpi: bool,
                                 status_code_infer_relevance: int,
                                 project_name: typing.Union[str, None],
                                 status_code_train_kpi: int, 
                                 cmd_output_expected: str,
                                 return_value_expected: bool,
                                 capsys: typing.Generator[CaptureFixture[str], None, None],
                                 router: Router):
    """Tests if kpi training fails and successfully starts

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    :param train_kpi: Flag for train kpi
    :type train_kpi: bool
    :param status_code_infer_relevance: Status code for infer relevance
    :type status_code_infer_relevance: int
    :param project_name: Project name
    :type project_name: typing.Union[str, None]
    :param status_code_train_kpi: Status code for train kpi
    :type status_code_train_kpi: int
    :param cmd_output_expected: Expected cmd output
    :type cmd_output_expected: str
    :param return_value_expected: Expected return_value
    :type return_value_expected: bool
    :param capsys: Requesting the default fixture capsys for capturing cmd outputs
    :type capsys: typing.Generator[CaptureFixture[str], None, None]
    """
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    mocked_server = prerequisites_run_router
    mocked_train_kpi_settings = Mock(train=train_kpi)
        
    # force an exception of generate_text_3434 by removing the folder_text_3434
    if not project_name:
        train_on_pdf.folder_text_3434 = None
    
    mocked_generate_text = Mock() 
    if project_name:
        if status_code_train_kpi < 0:
            mocked_generate_text.side_effect = lambda *args: True
        else:
            mocked_generate_text.side_effect = lambda *args: False
    else:
        mocked_generate_text.side_effect = Exception()
        
    with (patch('train_on_pdf.generate_text_3434', mocked_generate_text),
          patch.object(main_settings, 'train_kpi', mocked_train_kpi_settings)):
        mocked_server.get(f'http://{inference_ip}:{inference_port}/infer_relevance', status_code=status_code_infer_relevance)
        mocked_server.get(f'http://{inference_ip}:{inference_port}/train_kpi', status_code=status_code_train_kpi)
        return_value = router.run_router()

        cmd_output, _ = capsys.readouterr()
        assert cmd_output_expected in cmd_output
        assert return_value == return_value_expected


@pytest.mark.parametrize('infer_relevance, train_kpi',
                         [
                            (True, True),
                            (True, False),
                            (True, True),
                            (True, False),  
                         ])
def test_run_router_successful_run(prerequisites_run_router: requests_mock.mocker.Mocker,
                                   main_settings: MainSettings,
                                   s3_settings: S3Settings,
                                   infer_relevance: bool,
                                   train_kpi: bool,
                                   router: Router):
    """Tests a successful run of run_router

    :param prerequisites_run_router: Requesting the prerequisites_run_router fixture
    :type prerequisites_run_router: requests_mock.mocker.Mocker
    :param infer_relevance: Flag for infer relevance
    :type infer_relevance: bool
    :type train_kpi: Flag for train kpi
    :type train_kpi: bool
    """
    with patch('train_on_pdf.generate_text_3434', Mock()):
        return_value = router.run_router()

    assert return_value == True