from pathlib import Path
from train_on_pdf import run_router
import pytest
from unittest.mock import patch, Mock
import shutil
import train_on_pdf
import requests
import requests_mock
import typing
from tests.test_utils.test_convert_xls_to_csv import prerequisites_convert_xls_to_csv
from tests.test_utils.test_generate_text import prerequisites_generate_text


@pytest.fixture
def prerequisites_run_router(prerequisites_convert_xls_to_csv, 
                             prerequisites_generate_text
                             ) -> tuple[str, str, str, str]:
    """Prerequisites for running the function run_router

    :param prerequisites_convert_xls_to_csv: Requesting fixture for running function convert_xls_to_csv (required in 
    run_router)
    :param prerequisites_generate_text: Requesting fixture for running function generate_text (required in 
    run_router)
    :return: Return the strings as extraction ip, extraction port, inference ip and inference port
    :rtype: tuple[str, str, str, str]
    :yield: Return the strings as extraction ip, extraction port, inference ip and inference port
    :rtype: Iterator[tuple[str, str, str, str]]
    """
    extraction_ip = '0.0.0.0'
    extraction_port = '8000'
    inference_ip = '0.0.0.1'
    inference_port = '8000'

    with patch('train_on_pdf.convert_xls_to_csv', Mock()):
        yield extraction_ip, extraction_port, inference_ip, inference_port
    

@pytest.mark.parametrize('status_code, exptected_output',
                         [
                             (200, ('Extraction server is up. Proceeding to extraction.', None)),
                             (-1, ('Extraction server is not responding.', False))
                         ])
def test_run_router_extraction_liveness_up(status_code: int, 
                                           exptected_output: tuple[str, typing.Union[bool, None]],
                                           prerequisites_run_router: tuple[str, str, str, str], 
                                           capsys):
    """Tests the liveness of the extraction server

    :param status_code: Status code used for mocking the server
    :type status_code: int
    :param exptected_output: Expected output for checking correctness
    :type exptected_output: tuple[str, typing.Union[bool, None]]
    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]
    :param capsys: Requesting default fixture to capturing cmd output
    """
    extraction_ip, extraction_port, _, inference_port = prerequisites_run_router
    project_name = 'TEST'
    return_value = None
    
    try:
        with requests_mock.Mocker() as mock_server:
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=status_code)
            return_value = run_router(extraction_port, inference_port, project_name)
            
    except:
        exptected_cmd_output, expected_return_value = exptected_output
        cmd_output, cmd_error = capsys.readouterr()
        assert exptected_cmd_output in cmd_output
        assert return_value is expected_return_value

def test_run_router_extraction_server_down(prerequisites_run_router: tuple[str, str, str, str]):
    """Tests the return value if the extraction server is down

    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]]
    """
    extraction_ip, extraction_port, _, inference_port = prerequisites_run_router
    project_name = 'TEST'
    mock_project_settings = {}
    
    with (requests_mock.Mocker() as mock_server,
          patch('train_on_pdf.project_settings', mock_project_settings)):
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=-1)
        return_value = run_router(extraction_port, inference_port, project_name)

        # check sys out and return value
        assert return_value is False

def test_run_router_extraction_curation_server_down(prerequisites_run_router: tuple[str, str, str, str]):
    """Tests the return value of the curation of the extraction server

    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]]
    """
    extraction_ip, extraction_port, _, inference_port = prerequisites_run_router
    project_name = 'TEST'
    mock_project_settings = {}
    
    with (requests_mock.Mocker() as mock_server,
          patch('train_on_pdf.project_settings', mock_project_settings)):
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=-1)
        return_value = run_router(extraction_port, inference_port, project_name)

        # check sys out and return value
        assert return_value is False



@pytest.mark.parametrize('status_code, expected_output',
                         [
                             (200, 'Inference server is up. Proceeding to Inference.'),
                             (-1, 'Inference server is not responding.')
                         ]
                         )
def test_run_router_inference_liveness(status_code: int, 
                                       expected_output: tuple[str, typing.Union[bool, None]],
                                       prerequisites_run_router: tuple[str, str, str, str], 
                                       capsys):
    """Tests the liveness of the inference server, up as well as down

    :param status_code: Status code used for mocking the server
    :type status_code: int
    :param exptected_output: Expected output for checking correctness
    :type exptected_output: tuple[str, typing.Union[bool, None]]
    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]
    :param capsys: Requesting default fixture to capturing cmd output
    """
    extraction_ip, extraction_port, inference_ip, inference_port = prerequisites_run_router
    project_name = 'TEST'
    mock_project_settings = {}
    
    try:
        with (requests_mock.Mocker() as mock_server,
                patch('train_on_pdf.project_settings', mock_project_settings)):
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=200)
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=200)
            mock_server.get(f'http://{inference_ip}:{inference_port}/liveness', status_code=status_code)
            run_router(extraction_port, inference_port, project_name, infer_ip=inference_ip)
    
    except:    
        # check sys out and return value
        cmd_output, cmd_error = capsys.readouterr()
        assert expected_output in cmd_output

@pytest.mark.parametrize('mock_project_settings, status_code, expected_output',
                         [
                            ({'train_relevance': {'train': True}}, -1, ("Relevance training will be started.", False)),
                            ({'train_relevance': {'train': True}}, 200, ("Relevance training will be started.", None)),
                            ({'train_relevance': {'train': False}}, -1, (("No relevance training done. If you want to have a relevance training please "
                                         "set variable train under train_relevance to true."), None))
                         ]
)
def test_run_router_relevance_training(mock_project_settings: dict, 
                                       status_code: int, 
                                       expected_output: tuple[str, typing.Union[bool, None]],
                                       prerequisites_run_router: tuple[str, str, str, str], 
                                       capsys):
    """Tests if the relevance training fails and successfully starts

    :param mock_project_settings: Project settings used for mocking
    :type mock_project_settings: dict
    :param status_code: Status code used for mocking the server
    :type status_code: int
    :param exptected_output: Expected output for checking correctness
    :type exptected_output: tuple[str, typing.Union[bool, None]]
    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]
    :param capsys: Requesting default fixture to capturing cmd output
    """
    extraction_ip, extraction_port, inference_ip, inference_port = prerequisites_run_router
    project_name = 'TEST'
    return_value = None
    
    try:
        with (requests_mock.Mocker() as mock_server,
              patch('train_on_pdf.project_settings', mock_project_settings)):
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=200)
            mock_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=200)
            mock_server.get(f'http://{inference_ip}:{inference_port}/liveness', status_code=200)
            mock_server.get(f'http://{inference_ip}:{inference_port}/train_relevance', status_code=status_code)
            return_value = run_router(extraction_port, inference_port, project_name, infer_ip=inference_ip)
    except:
        pass
    finally:
        # check sys out and return value
        cmd_output, _ = capsys.readouterr()
        expected_cmd_out, exptected_return_value = expected_output
        assert expected_cmd_out in cmd_output
        assert return_value == exptected_return_value


@pytest.mark.parametrize('mock_project_settings, status_code_infer_relevance, project_name, status_code_train_kpi, expected_output',
                         [
                            ({'train_kpi': {'train': True}}, -1, "TEST", -1, ("", False)),
                            ({'train_kpi': {'train': True}}, 200, "TEST", -1, ("text_3434 was generated without error", False)),
                            ({'train_kpi': {'train': True}}, 200, "TEST", 200, ("text_3434 was not generated without error", True)),
                            ({'train_kpi': {'train': True}}, 200, None, -1, ("Error while generating text_3434.", False)),
                            ({'train_kpi': {'train': True}}, 200, None, 200, ("Error while generating text_3434.", True)),
                            ({'train_kpi': {'train': False}}, -1, None, -1, (("No kpi training done. If you want to have a kpi "
                                                                    "training please set variable train under train_kpi to true."), True))
                         ]
)
def test_run_router_kpi_training(mock_project_settings: typing.Dict[str, typing.Dict[str, bool]], 
                                 status_code_infer_relevance: int, 
                                 project_name: typing.Union[str, None],
                                 status_code_train_kpi: int, 
                                 expected_output: tuple[str, bool], 
                                 prerequisites_run_router: tuple[str, str, str, str], 
                                 capsys):
    """Tests if kpi training fails and successfully starts

    :param mock_project_settings: Project settings used for mocking
    :type mock_project_settings: typing.Dict[str, typing.Dict[str, bool]]
    :param status_code_infer_relevance: Status code used for mocking the server
    :type status_code_infer_relevance: int
    :param project_name: Name of the project
    :type project_name: typing.Union[str, None]
    :param status_code_train_kpi: Status code used for mocking the server
    :type status_code_train_kpi: int
    :param exptected_output: Expected output for checking correctness
    :type expected_output: tuple[str, bool]
    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]
    :param capsys: Requesting default fixture to capturing cmd output
    """
    extraction_ip, extraction_port, inference_ip, inference_port = prerequisites_run_router
    return_value = None
    mock_project_settings['train_relevance'] = {'train': False}
    mock_project_settings['s3_usage'] = None
    mock_project_settings['s3_settings'] = None
        
    # force an exception of generate_text_3434 by remove the folder_text_3434
    if not project_name:
        train_on_pdf.folder_text_3434 = None
    
    mocked_generate_text = Mock() 
    if project_name:
        if status_code_train_kpi < 0:
            mocked_generate_text.side_effect = lambda *args: True
        else:
            mocked_generate_text.side_effect = lambda *args: False
    else:
        mocked_generate_text.side_effect = Exception
        
    with (requests_mock.Mocker() as mock_server,
        patch('train_on_pdf.project_settings', mock_project_settings),
        patch('train_on_pdf.generate_text_3434', mocked_generate_text)):
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/liveness', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/train_relevance', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/infer_relevance', status_code=status_code_infer_relevance)
        mock_server.get(f'http://{inference_ip}:{inference_port}/train_kpi', status_code=status_code_train_kpi)
        return_value = run_router(extraction_port, inference_port, project_name, infer_ip=inference_ip)

    # check sys out and return value
    cmd_output, _ = capsys.readouterr()
    expected_cmd_out, exptected_return_value = expected_output
    assert expected_cmd_out in cmd_output
    assert return_value == exptected_return_value

@pytest.mark.parametrize('mock_project_settings, expected_output',
                         [
                            ({'train_relevance': {'train': True}, 'train_kpi': {'train': True}}, True),
                            ({'train_relevance': {'train': True}, 'train_kpi': {'train': False}}, True),
                            ({'train_relevance': {'train': False}, 'train_kpi': {'train': True}}, True),
                            ({'train_relevance': {'train': False}, 'train_kpi': {'train': False}}, True),  
                         ]
)
def test_run_router_successful_run(mock_project_settings: typing.Dict[str, typing.Dict[str, bool]], 
                                   expected_output: bool, 
                                   prerequisites_run_router: tuple[str, str, str, str]):
    """Tests a successful run of run_router

    :param mock_project_settings: Project settings used for mocking
    :type mock_project_settings: typing.Dict[str, typing.Dict[str, bool]]
    :param expected_output:  Expected output for checking correctness
    :type expected_output: bool
    :param prerequisites_run_router: Requesting prerequisites fixture for run_router
    :type prerequisites_run_router: tuple[str, str, str, str]
    """
    extraction_ip, extraction_port, inference_ip, inference_port = prerequisites_run_router
    project_name = 'TEST'
     
    with (requests_mock.Mocker() as mock_server,
        patch('train_on_pdf.project_settings', mock_project_settings)):
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/liveness', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/extract', status_code=200)
        mock_server.get(f'http://{extraction_ip}:{extraction_port}/curate', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/liveness', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/train_relevance', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/infer_relevance', status_code=200)
        mock_server.get(f'http://{inference_ip}:{inference_port}/train_kpi', status_code=200)
        return_value = run_router(extraction_port, inference_port, project_name, infer_ip=inference_ip)

    # check for return value
    exptected_return_value = expected_output
    assert return_value == exptected_return_value
