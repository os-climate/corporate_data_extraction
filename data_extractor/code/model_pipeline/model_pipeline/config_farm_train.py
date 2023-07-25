import pathlib
import os
from farm.modeling.prediction_head import TextClassificationHead
import torch
from logging import getLogger, WARNING, INFO, DEBUG

_logger = getLogger(__name__)
LOGGING_MAPPING = {"info": INFO, "warning": WARNING, "debug": DEBUG}

class Config:

    def __init__(self, project_name, output_model_name=None, experiment_type="RELEVANCE", data_type="Text"):
        self.root = str(pathlib.Path(__file__).resolve().parent.parent.parent.parent) 
        self.experiment_type = experiment_type
        self.output_model_name = output_model_name
        self.experiment_name = project_name  
        self.data_type = data_type  # Text | Table
        farm_infer_logging_level = "warning"  # FARM logging level during inference; supports info, warning, debug
        self.farm_infer_logging_level = LOGGING_MAPPING[farm_infer_logging_level]


class FileConfig(Config):

    def __init__(self,project_name, output_model_name):
        super().__init__(project_name, output_model_name)
        self.data_dir = os.path.join(self.root, "data")
        self.annotation_dir = os.path.join(self.data_dir, self.experiment_name, "interim", "ml", "annotations")
        self.curated_data = os.path.join(self.data_dir, self.experiment_name, "interim", "ml", "curation", "esg_TEXT_dataset.csv")
        self.training_dir = os.path.join(self.data_dir, self.experiment_name, "interim", "ml",  "training")
        self.train_filename = os.path.join(self.training_dir, f"kpi_train_split.csv")
        self.dev_filename = os.path.join(self.training_dir, f"kpi_val_split.csv")
        self.test_filename = None
        #The next defines the folder where the trained relevance model is stored to
        self.saved_models_dir = os.path.join(self.root, "models", self.experiment_name, self.experiment_type, self.data_type, self.output_model_name)
        

class TokenizerConfig(Config):

    def __init__(self,project_name):
        super().__init__(project_name)
        self.pretrained_model_name_or_path = "roberta-base"
        self.do_lower_case = False


class ProcessorConfig(Config):

    def __init__(self,project_name):
        super().__init__(project_name)
        if self.experiment_type == "RELEVANCE":
            self.processor_name = "TextPairClassificationProcessor"
        else:
            raise ValueError("No existing processor for this task")
        self.load_dir = os.path.join(self.root, "models", "base" , "relevance_roberta")
        # set to None if you don't want to load the\
        # vocab.json file
        self.max_seq_len = 512
        self.dev_split = .2
        self.label_list = ["0", "1"]
        self.label_column_name = "label"  # label column name in data files
        self.delimiter = ','
        self.metric = "acc"


class ModelConfig(Config):

    def __init__(self,project_name):
        super().__init__(project_name)
        if self.experiment_type == "RELEVANCE":
            self.class_type = TextClassificationHead
            self.head_config = {
                "num_labels": 2
            }
        else:
            raise ValueError("No existing model for this task")
        # set to None if you don't want to load the config file for this model
        self.load_dir = os.path.join(self.root, "models", "base",
                                     "relevance_roberta")  # relevance_roberta | relevance_roberta_table_headers
        self.lang_model = "roberta-base"
        self.layer_dims = [768, 2]
        self.lm_output_types = ["per_sequence"]  # or ["per_tokens"]


class TrainingConfig(Config):

    def __init__(self,project_name, seed):
        super().__init__(project_name)

        self.seed = seed
        self.run_hyp_tuning = False
        self.use_cuda = True

        # Check if GPU exists
        if not torch.cuda.is_available():
            _logger.warning("No gpu available, setting use_cuda to False")
            self.use_cuda = False

        self.use_amp = True
        self.distributed = False
        self.learning_rate = 1e-5
        self.n_epochs = 10
        self.evaluate_every = 30
        self.dropout = 0.1
        self.batch_size = 1
        self.grad_acc_steps = 1
        self.run_cv = False  # running cross-validation won't save a model
        self.xval_folds = 5


class MLFlowConfig(Config):

    def __init__(self,project_name):
        super().__init__(project_name)
        self.track_experiment = False
        self.run_name = self.experiment_name
        self.url = "http://localhost:5000"


class InferConfig(Config):

    def __init__(self, project_name, output_model_name):
        super().__init__(project_name, output_model_name)
        # please change the following accordingly
        self.data_types = ['Text']  # ["Text", "Table"] supported "Text", "Table"
        self.load_dir = {"Text": os.path.join(self.root, "models", self.experiment_name, self.experiment_type, self.data_type, self.output_model_name)}

        # Use the following for the pre-trained models inside Docker
        # oneqbit_checkpoint_dir = os.path.join(self.root, "model_pipeline", "saved_models", "1QBit_Pretrained_ESG")
        # self.load_dir = {"Text": os.path.join(oneqbit_checkpoint_dir, "esg_text_checkpoint"),
        #                 "Table": os.path.join(oneqbit_checkpoint_dir, "esg_table_checkpoint")}
        self.skip_processed_files = True  # If set to True, will skip inferring on already processed files
        self.batch_size = 16
        self.gpu = True
        self.num_processes = None   # Set to value of 1 (or 0) to disable multiprocessing.
                              # Set to None to let Inferencer use all CPU cores minus one.
        self.disable_tqdm = True # To not see the progress bar at inference time, set to True
        self.extracted_dir = os.path.join(self.root, "data",  self.experiment_name, "interim", "ml", "extraction")
        self.result_dir = {"Text": os.path.join(self.root, "data", self.experiment_name, "output", self.experiment_type, self.data_type)}
        self.kpi_questions = []
        # set to  ["OG", "CM", "CU"] for KPIs of all sectors.
        self.sectors = ["OG", "CM", "CU"]  #["UT"]
        self.return_class_probs = False
