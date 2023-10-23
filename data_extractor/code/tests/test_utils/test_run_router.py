import typing
from unittest.mock import patch, Mock
import pytest
import requests_mock
import train_on_pdf
from tests.test_utils.test_generate_text import prerequisites_generate_text
from utils.s3_communication import S3Communication
from utils.settings import S3Settings, MainSettings
from utils.router import Router

from _pytest.capture import CaptureFixture

@pytest.fixture
def router(main_settings: MainSettings, s3_settings: S3Settings):
    dict_general_settings = {'project_name': 'TEST',
                             'ext_ip': '0.0.0.0', 
                             'ext_port': '8000',
                             'infer_ip': '0.0.0.1', 
                             'infer_port': '8000'}

    with (patch.object(main_settings, 'general', Mock(**dict_general_settings))):
        router = Router(main_settings=main_settings, s3_settings=s3_settings)
        router._set_extraction_server_string()
        router._set_inference_server_string()
        yield router

@pytest.fixture
def server(prerequisites_generate_text) -> requests_mock.mocker.Mocker:
    """Prerequisites for running the function run_router

    :param prerequisites_generate_text: Requesting fixture for running function generate_text (required in 
    run_router)
    :rtype: requests_mock.mocker.Mocker
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    server_address_extraction = f'http://{extraction_ip}:{extraction_port}'
    server_address_inference = f'http://{inference_ip}:{inference_port}'
    
    with (requests_mock.Mocker() as mocked_server,
          patch('train_on_pdf.json')):
        mocked_server.get(f'{server_address_extraction}/liveness', status_code=200)
        mocked_server.get(f'{server_address_extraction}/extract', status_code=200)
        mocked_server.get(f'{server_address_extraction}/curate', status_code=200)
        mocked_server.get(f'{server_address_inference}/liveness', status_code=200)
        mocked_server.get(f'{server_address_inference}/train_relevance', status_code=200)
        mocked_server.get(f'{server_address_inference}/infer_relevance', status_code=200)
        mocked_server.get(f'{server_address_inference}/train_kpi', status_code=200)
        yield mocked_server
    

@pytest.mark.parametrize('status_code, cmd_output_expected, return_value_expected',
                         [(200, 'Extraction server is up. Proceeding to extraction.', True),
                          (-1, 'Extraction server is not responding.', False)])
def test_run_router_extraction_liveness_up(router: Router,
                                           server: requests_mock.mocker.Mocker,
                                           status_code: int, 
                                           cmd_output_expected: str,
                                           return_value_expected: bool,
                                           capsys: typing.Generator[CaptureFixture[str], None, None]): 
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    server_address_node = f'http://{extraction_ip}:{extraction_port}/liveness'
    
    server.get(server_address_node, status_code=status_code)
    router._check_extraction_server_is_live()

    cmd_output, _ = capsys.readouterr()
    assert cmd_output_expected in cmd_output
    assert router._return_value == return_value_expected


def test_run_router_extraction_server_down(router: Router,
                                           server: requests_mock.mocker.Mocker,
                                           capsys: typing.Generator[CaptureFixture[str], None, None]):
    """Tests the return value if the extraction server is down

    :param server: Requesting the server fixture
    :type server: requests_mock.mocker.Mocker
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    server_address_node = f'http://{extraction_ip}:{extraction_port}/extract'
    server.get(server_address_node, status_code=-1)
    
    router._send_payload_to_server_address_with_node(f'http://{extraction_ip}:{extraction_port}', 'extract')

    assert router._return_value is False


def test_run_router_extraction_curation_server_down(router: Router,
                                                    server: requests_mock.mocker.Mocker):
    """Tests the return value of the curation of the extraction server

    :param server: Requesting the server fixture
    :type server: requests_mock.mocker.Mocker
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    server_address_node = f'http://{extraction_ip}:{extraction_port}/curate'
    
    server.get(server_address_node, status_code=-1)      
    router.run_router()

    assert router._return_value is False


@pytest.mark.parametrize('status_code, cmd_output_expected, return_value_expected',
                         [(200, 'Inference server is up. Proceeding to Inference.', True),
                          (-1, 'Inference server is not responding.', False)])
def test_run_router_inference_liveness(router: Router,
                                       server: requests_mock.mocker.Mocker,
                                       status_code: int, 
                                       cmd_output_expected: str,
                                       return_value_expected: bool,
                                       capsys: typing.Generator[CaptureFixture[str], None, None]):
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    server_address_node = f'http://{inference_ip}:{inference_port}/liveness'

    server.get(server_address_node, status_code=status_code)
    router._check_inference_server_is_live()
    
    cmd_output, _ = capsys.readouterr()
    assert cmd_output_expected in cmd_output
    assert router._return_value == return_value_expected


@pytest.mark.parametrize('train_relevance, status_code, cmd_output_expected, return_value_expected',
                         [(True, -1, "Relevance training will be started.", False),
                          (True, 200, "Relevance training will be started.", True),
                          (False, -1, ("No relevance training done. If you want to have a relevance training please "
                                         "set variable train under train_relevance to true."), True)])
def test_run_router_relevance_training(router: Router,
                                       server: requests_mock.mocker.Mocker,
                                       main_settings: MainSettings,
                                       train_relevance: bool, 
                                       status_code: int,
                                       cmd_output_expected: str,
                                       return_value_expected: bool, 
                                       capsys: typing.Generator[CaptureFixture[str], None, None]):
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    server_address_node = f'http://{inference_ip}:{inference_port}/train_relevance'

    with patch.object(main_settings, 'train_relevance', Mock(train=train_relevance)):
        server.get(server_address_node, status_code=status_code)
        router.run_router()

    cmd_output, _ = capsys.readouterr()
    assert cmd_output_expected in cmd_output
    assert router._return_value == return_value_expected


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
def test_run_router_kpi_training(router: Router,
                                 server: requests_mock.mocker.Mocker,
                                 main_settings: MainSettings,
                                 train_kpi: bool,
                                 status_code_infer_relevance: int,
                                 project_name: typing.Union[str, None],
                                 status_code_train_kpi: int, 
                                 cmd_output_expected: str,
                                 return_value_expected: bool,
                                 capsys: typing.Generator[CaptureFixture[str], None, None]):
    inference_ip = '0.0.0.1'
    inference_port = '8000'
    server_address_node_infer_relevance = f'http://{inference_ip}:{inference_port}/infer_relevance'
    server_address_node_train_kpi = f'http://{inference_ip}:{inference_port}/train_kpi'
        
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
          patch.object(main_settings, 'train_kpi', Mock(train=train_kpi))):
        server.get(server_address_node_infer_relevance, status_code=status_code_infer_relevance)
        server.get(server_address_node_train_kpi, status_code=status_code_train_kpi)
        router.run_router()

        cmd_output, _ = capsys.readouterr()
        assert cmd_output_expected in cmd_output
        assert router._return_value == return_value_expected


@pytest.mark.parametrize('infer_relevance, train_kpi',
                         [
                            (True, True),
                            (True, False),
                            (True, True),
                            (True, False),  
                         ])
def test_run_router_successful_run(router: Router,
                                   server: requests_mock.mocker.Mocker,
                                   infer_relevance: bool,
                                   train_kpi: bool):
    with patch('train_on_pdf.generate_text_3434', Mock()):
        router.run_router()

    assert router._return_value == True