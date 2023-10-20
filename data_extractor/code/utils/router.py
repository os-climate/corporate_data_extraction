from pathlib import Path
import requests
from utils.s3_communication import S3Communication
from utils.settings import S3Settings, MainSettings
from utils.xls_to_csv_converter import XlsToCsvConverter
from utils.core_utils import download_data_from_s3_main_bucket_to_local_folder_if_required,\
upload_data_from_local_folder_to_s3_interim_bucket_if_required
import train_on_pdf
import traceback
import json


class Router:
    def __init__(self, 
                 main_settings: MainSettings | None = None, 
                 s3_settings: S3Settings | None = None,
                 converter: XlsToCsvConverter | None = None, 
                 s3c_main: S3Communication | None = None, 
                 s3c_interim: S3Communication | None = None,
                 source_annotation: Path = Path('input/annotations'),
                 destination_annotation: Path = Path('interim/ml/annotations')) -> None:
        self._main_settings: MainSettings = main_settings
        self._s3_settings: S3Settings = s3_settings
        self._converter: XlsToCsvConverter = converter
        self._source_annotation: Path = source_annotation
        self._destination_annotation: Path = destination_annotation
        self._s3_controller_main: S3Communication = s3c_main
        self._s3_controller_interim: S3Communication = s3c_interim
        self.extraction_server_address: str = None
        self.inference_server_address: str = None
        self._return_value: bool = True
        self._payload: dict = {}

    
    def run_router(self):
        self._set_extraction_server_string()
        self._set_inference_server_string()
        # self._convert_xls_to_csv()
        
        self._check_extraction_server_is_live()
        self._define_payload()

        self._send_payload_to_server_address_with_node(self._extraction_server_address, 'extract')
        self._send_payload_to_server_address_with_node(self._extraction_server_address, 'curate')
        
        self._check_inference_server_is_live()

        self._check_for_train_relevance_training_and_send_request()
        self._check_for_kpi_training_and_send_request()

        return self._return_value

    
    def _set_extraction_server_string(self):
        self._extraction_server_address = f'http://{self._main_settings.general.ext_ip}:{self._main_settings.general.ext_port}'


    def _set_inference_server_string(self):
        self._inference_server_address = f'http://{self._main_settings.general.infer_ip}:{self._main_settings.general.infer_port}'


    def _convert_xls_to_csv(self):
        download_data_from_s3_main_bucket_to_local_folder_if_required(self._s3_controller_main, self._source_annotation, Path(self._s3_settings.prefix) / Path('input/annotations'))
        self._converter.convert()
        upload_data_from_local_folder_to_s3_interim_bucket_if_required(self._s3_controller_interim, self._destination_annotation, Path(self._s3_settings.prefix) / Path('interim/ml/annotations'))


    def _send_payload_to_server_address_with_node(self, server_address: str, node: str):
        response = requests.get(f'{server_address}/{node}', params=self._payload)
        print(response.text)
        if response.status_code != 200:
            self._return_value = False
    
    def _check_extraction_server_is_live(self):
        response = requests.get(f"{self._extraction_server_address}/liveness")
        if response.status_code == 200:
            print("Extraction server is up. Proceeding to extraction.")
        else:
            print("Extraction server is not responding.")
            self._return_value = False

    def _define_payload(self):
        self._payload = {'project_name': self._main_settings.general.project_name, 'mode': 'train'}
        self._payload.update(self._main_settings.model_dump())
        self._payload = {'payload': json.dumps(self._payload)}


    def _check_inference_server_is_live(self):
        response = requests.get(f"{self._inference_server_address}/liveness")
        if response.status_code == 200:
            print("Inference server is up. Proceeding to Inference.")
        else:
            print("Inference server is not responding.")
            self._return_value = False
            
    def _check_for_train_relevance_training_and_send_request(self):
        print("Relevance training will be started.")
        if self._main_settings.train_relevance.train:
            self._send_payload_to_server_address_with_node(self._inference_server_address, 'train_relevance')
        else:
            print("No relevance training done. If you want to have a relevance training please set variable "
              "train under train_relevance to true.")
    

    def _check_for_kpi_training_and_send_request(self):
        if self._main_settings.train_kpi.train:
            self._send_payload_to_server_address_with_node(self._inference_server_address, 'infer_relevance')
            self._check_for_generate_text_3434()
            print('Next we start the training of the inference model. This may take some time.')
            self._send_payload_to_server_address_with_node(self._inference_server_address, 'train_kpi')
        else:
            print("No kpi training done. If you want to have a kpi training please set variable"
              " train under train_kpi to true.")    
        

    def _check_for_generate_text_3434(self):
        try:
            temp = train_on_pdf.generate_text_3434(self._main_settings.general.project_name, 
                                      self._s3_settings.s3_usage, self._s3_settings)
            if temp:
                print('text_3434 was generated without error.')
            else:
                print('text_3434 was not generated without error.')
        except Exception as e:
            print('Error while generating text_3434.')
            print(repr(e))
            print(traceback.format_exc())

        
    


def run_router(main_settings: MainSettings, s3_settings: S3Settings,
               converter: XlsToCsvConverter, s3c_main=None, s3c_interim=None,
               source_annotation: Path=Path('input/annotations'),
               destination_annotation: Path=Path('interim/ml/annotations')):
    """
    Router function
    It fist sends a command to the extraction server to begin extraction.
    If done successfully, it will send a command to the inference server to start inference.
    :param ext_port: int: The port that the extraction server is listening on
    :param infer_port: int: The port that the inference server is listening on
    :param project_name: string
    :param ext_ip: int: The ip that the extraction server is listening on
    :param infer_ip: int: The ip that the inference server is listening on
    :param s3_usage: boolean: True if S3 connection should be used
    :param s3c_main: S3Communication class element (based on boto3)
    :param s3c_interim: S3Communication class element (based on boto3)
    :return: A boolean, indicating success
    """
    router = Router(main_settings, s3_settings, converter)
    return router.run_router()
    

    # port_extraction_server = main_settings.general.ext_port
    # ip_extraction_server = main_settings.general.ext_ip
    # port_inference_server = main_settings.general.infer_port
    # ip_inference_server = main_settings.general.infer_ip
    # project_name = main_settings.general.project_name
    
    # download_data_from_s3_main_bucket_to_local_folder_if_required(s3c_main, source_annotation, Path(s3_settings.prefix) / Path('input/annotations'))
    # converter.convert()
    # upload_data_from_local_folder_to_s3_interim_bucket_if_required(s3c_interim, destination_annotation, Path(s3_settings.prefix) / Path('interim/ml/annotations'))
    
    # # Check if the extraction server is live
    # ext_live = requests.get(f"http://{ip_extraction_server}:{port_extraction_server}/liveness")
    # if ext_live.status_code == 200:
    #     print("Extraction server is up. Proceeding to extraction.")
    # else:
    #     print("Extraction server is not responding.")
    #     return False
    
    # payload = {'project_name': project_name, 'mode': 'train'}
    # payload.update(main_settings.model_dump())
    # payload = {'payload': json.dumps(payload)}
    
    # # Sending an execution request to the extraction server for extraction
    # ext_resp = requests.get(f"http://{ip_extraction_server}:{port_extraction_server}/extract", params=payload)
    # print(ext_resp.text)
    # if ext_resp.status_code != 200:
    #     return False
    
    # # Sending an execution request to the extraction server for curation
    # ext_resp = requests.get(f"http://{ip_extraction_server}:{port_extraction_server}/curate", params=payload)
    # print(ext_resp.text)
    # if ext_resp.status_code != 200:
    #     return False
    
    # # Check if the inference server is live
    # infer_live = requests.get(f"http://{ip_inference_server}:{port_inference_server}/liveness")
    # if infer_live.status_code == 200:
    #     print("Inference server is up. Proceeding to Inference.")
    # else:
    #     print("Inference server is not responding.")
    #     return False
    
    # if main_settings.train_relevance.train:
    #     print("Relevance training will be started.")
    #     # Requesting the inference server to start the relevance stage
    #     train_resp = requests.get(f"http://{ip_inference_server}:{port_inference_server}/train_relevance", params=payload)
    #     print(train_resp.text)
    #     if train_resp.status_code != 200:
    #         return False
    # else:
    #     print("No relevance training done. If you want to have a relevance training please set variable "
    #           "train under train_relevance to true.")
    
    # if main_settings.train_kpi.train:
    #     # Requesting the inference server to start the relevance stage
    #     infer_resp = requests.get(f"http://{ip_inference_server}:{port_inference_server}/infer_relevance", params=payload)
    #     print(infer_resp.text)
    #     if infer_resp.status_code != 200:
    #         return False
    #     try:
    #         temp = generate_text_3434(project_name, s3_settings.s3_usage, s3_settings)
    #         if temp:
    #             print('text_3434 was generated without error.')
    #         else:
    #             print('text_3434 was not generated without error.')
    #     except Exception as e:
    #         print('Error while generating text_3434.')
    #         print(repr(e))
    #         print(traceback.format_exc())

    #     print('Next we start the training of the inference model. This may take some time.')
    #     # Requesting the inference server to start the kpi extraction stage
    #     infer_resp_kpi = requests.get(f"http://{ip_inference_server}:{port_inference_server}/train_kpi", params=payload)
    #     print(infer_resp_kpi.text)
    #     if infer_resp_kpi.status_code != 200:
    #         return False
    # else:
    #     print("No kpi training done. If you want to have a kpi training please set variable"
    #           " train under train_kpi to true.")
    # return True
