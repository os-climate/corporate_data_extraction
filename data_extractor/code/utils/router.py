import requests
from utils.settings import S3Settings, MainSettings, Settings
from utils.utils import generate_text_3434
from utils.paths import ProjectPaths
import traceback
import json


class Router:
    def __init__(self, 
                 main_settings: Settings, 
                 s3_settings: Settings,
                 project_paths: ProjectPaths) -> None:
        self._main_settings: Settings = main_settings
        self._s3_settings: Settings = s3_settings
        self._project_paths: ProjectPaths = project_paths
        self._extraction_server_address: str = ''
        self._inference_server_address: str = ''
        self._return_value: bool = True
        self._payload: dict = {}

    @property
    def return_value(self) -> bool:
        return self._return_value
    
    def run_router(self):
        self._set_extraction_server_string()
        self._set_inference_server_string()
        
        self._check_extraction_server_is_live()
        self._define_payload()

        self._send_payload_to_server_address_with_node(self._extraction_server_address, 'extract')
        self._send_payload_to_server_address_with_node(self._extraction_server_address, 'curate')
        
        self._check_inference_server_is_live()

        self._check_for_train_relevance_training_and_send_request()
        self._check_for_kpi_training_and_send_request()

    
    def _set_extraction_server_string(self):
        self._extraction_server_address: str = f'http://{self._main_settings.general.ext_ip}:{self._main_settings.general.ext_port}'


    def _set_inference_server_string(self):
        self._inference_server_address: str = f'http://{self._main_settings.general.infer_ip}:{self._main_settings.general.infer_port}'


    def _send_payload_to_server_address_with_node(self, server_address: str, node: str):
        response: requests.Response = requests.get(f'{server_address}/{node}', params=self._payload)
        print(response.text)
        if response.status_code != 200:
            self._return_value: bool = False


    def _check_extraction_server_is_live(self):
        response: requests.Response = requests.get(f"{self._extraction_server_address}/liveness")
        if response.status_code == 200:
            print("Extraction server is up. Proceeding to extraction.")
        else:
            print("Extraction server is not responding.")
            self._return_value: bool = False


    def _define_payload(self):
        self._payload: dict[str] = {'project_name': self._main_settings.general.project_name, 'mode': 'train'}
        self._payload.update(self._main_settings.model_dump())
        self._payload: dict[str] = {'payload': json.dumps(self._payload)}


    def _check_inference_server_is_live(self):
        response: requests.Response = requests.get(f"{self._inference_server_address}/liveness")
        if response.status_code == 200:
            print("Inference server is up. Proceeding to Inference.")
        else:
            print("Inference server is not responding.")
            self._return_value: bool = False


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
            temp: bool = generate_text_3434(self._main_settings.general.project_name, 
                                            self._s3_settings.s3_usage, self._s3_settings, self._project_paths)
            if temp:
                print('text_3434 was generated without error.')
            else:
                print('text_3434 was not generated without error.')
        except Exception as e:
            print('Error while generating text_3434.')
            print(repr(e))
            print(traceback.format_exc())
