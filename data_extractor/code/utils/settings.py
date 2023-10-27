from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from typing import List


class Settings():
    pass

class General(BaseSettings):
    project_name: str = 'TEST'
    ext_ip: str = '172.30.15.68'
    ext_port: str = '4000'
    infer_ip: str = '172.30.88.213'
    infer_port: str = '6000'
    rb_ip: str = '172.30.224.91'
    rb_port: int = 8000
    delete_interim_files: bool = True

class DataExport(BaseSettings):
    enable_db_export: bool = False
    db_dialect: str = 'oracle'
    db_sql_driver: str = 'cx_oracle'
    db_host: str = ''
    db_port: str = '1521'
    db_user: str = ''
    db_password: str = ''
    db_post_command: str = ''

class Extraction(BaseSettings):
    min_paragraph_length: int = 20
    seed: int = 42
    annotation_folder: str | None = None
    skip_extracted_files: bool = True
    use_extractions: bool = True
    store_extractions: bool = True

class Curation(BaseSettings):
    retrieve_paragraph: bool = False
    neg_pos_ratio: int = 1
    columns_to_read: List[str] = ['company', 'source_file', 'source_page', 'kpi_id', 'year', 'answer', 'data_type', 'relevant_paragraphs']
    company_to_exclude: List[str] = []
    create_neg_samples: bool = True
    min_length_neg_sample: int = 50
    seed: int = 41

class Processor(BaseSettings):
    proc_max_seq_len: int = 512
    proc_dev_split: float = 0.2
    proc_label_list: List[str] = ['0', '1']
    proc_label_column_name: str = 'label'
    proc_delimiter: str = ','
    proc_metric: str = 'acc'

class Model(BaseSettings):
    model_config = ConfigDict(protected_namespaces=('settings_',))
    model_layer_dims: List[int] = [768, 2]
    model_lm_output_types: List[str] = ['per_sequence']
    
class Training(BaseSettings):
    run_hyp_tuning: bool = False
    use_amp: bool = True
    distributed: bool = False
    learning_rate: float = 1.0e-05
    n_epochs: int = 10
    evaluate_every: int = 100
    dropout: float = 0.2
    batch_size: int = 4
    grad_acc_steps: int = 1
    run_cv: bool = False
    xval_folds: int = 5
    metric: str | None = None
    max_processes: int = 128

class TrainRelevance(BaseSettings):
    base_model: str = 'roberta-base'
    input_model_name: str | None = '' 
    output_model_name: str = 'TEST_1'
    train: bool = True
    seed: int = 42
    processor: Processor = Processor()
    model: Model = Model()
    training: Training = Training()

class InferRelevance(BaseSettings):
    skip_processed_files: bool = True
    batch_size: int = 16
    gpu: bool = True
    num_processes: int | None = None
    disable_tqdm: bool = True
    kpi_questions: List[str] = []
    sectors: List[str] = ["OG", "CM", "CU"]
    return_class_probs: bool = False

class KpiCuration(BaseSettings):
    val_ratio: int = 0
    seed: int = 42
    find_new_answerable: bool = True
    create_unanswerable: bool = True


class Data(BaseSettings):
    perform_splitting: bool = True
    dev_split: float = 0.2
    
class MlFlow(BaseSettings):
    track_experiment: bool = False
    url: str = 'http://localhost:5000'

class KpiProcessor(BaseSettings):
    max_seq_len: int = 384
    label_list: List[str] = ["start_token", "end_token"]
    metric: str = 'squad'

class TrainKpi(BaseSettings):
    input_model_name: str | None = None
    output_model_name: str = 'TEST_1'
    base_model: str = 'a-ware/roberta-large-squadv2'
    train: bool = True
    seed: int = 42
    curation: KpiCuration = KpiCuration()
    data: Data = Data()
    mlflow: MlFlow = MlFlow()
    processor: KpiProcessor = KpiProcessor()
    model: Model = Model(model_lm_output_types=["per_token"])
    training: Training = Training(dropout=0.3, metric='f1', max_processes=1)
    
class InferKpi(BaseSettings):
    skip_processed_files: bool = False # If set to True, will skip inferring on already processed files
    top_k: int = 4
    batch_size: int = 16
    gpu: bool = True
    num_processes: int | None = None # Set to value 1 (or 0) to disable multiprocessing. Set to None to let Inferencer use all CPU cores minus one.
    no_ans_boost: int = -15 # If incr
    
class RuleBased(BaseSettings):
    verbosity: int = 2
    use_docker: bool = True

class MainSettings(Settings, BaseSettings):
    general: General = General()
    data_export: DataExport = DataExport()
    extraction: Extraction = Extraction()
    curation: Curation = Curation()
    train_relevance: TrainRelevance = TrainRelevance()
    infer_relevance: InferRelevance = InferRelevance()
    train_kpi: TrainKpi = TrainKpi()
    infer_kpi: InferKpi = InferKpi()
    rule_based: RuleBased = RuleBased()


class MainBucketSettings(BaseSettings):
    s3_endpoint: str = Field(default='', alias='LANDING_AWS_ENDPOINT')
    s3_access_key: str = Field(default='', alias='LANDING_AWS_ACCESS_KEY')
    s3_secret_key: str = Field(default='', alias='LANDING_AWS_SECRET_KEY')
    s3_bucket_name: str = Field(default='', alias='LANDING_AWS_BUCKET_NAME')

class InterimBucketSettings(BaseSettings):
    s3_endpoint: str = Field(default='', alias='INTERIM_AWS_ENDPOINT')
    s3_access_key: str = Field(default='', alias='INTERIM_AWS_ACCESS_KEY')
    s3_secret_key: str = Field(default='', alias='INTERIM_AWS_SECRET_KEY')
    s3_bucket_name: str = Field(default='', alias='INTERIM_AWS_BUCKET_NAME')
    
class S3Settings(Settings, BaseSettings):
    prefix: str = Field(default='corporate_data_extraction_projects')
    main_bucket: MainBucketSettings = MainBucketSettings()
    interim_bucket: InterimBucketSettings = InterimBucketSettings()
    s3_usage: bool | None = False
    

_current_settings_main: MainSettings | None = None
_current_settings_s3: S3Settings | None = None
    
    
def get_main_settings() -> MainSettings:
    if _current_settings_main is None:
        setup_main_settings()
        return _current_settings_main
    else:
        return _current_settings_main
        
def setup_main_settings():
    global _current_settings_main
    _current_settings_main = MainSettings()
    
def get_s3_settings() -> S3Settings:
    if _current_settings_s3 is None:
        setup_s3_settings()
        return _current_settings_s3
    else:
        return _current_settings_s3
        
def setup_s3_settings():
    global _current_settings_s3
    _current_settings_s3 = S3Settings()


# def get_s3_settings() -> S3Settings:
#     return _current_settings_s3