from pathlib import Path  
from config import get_config

config = get_config()  

# =============================================================================
# /PROJECT_DATA_DIR/input
# =============================================================================
path_input = Path('input')
source_pdf = path_input / 'pdfs' / 'training'
source_annotation = path_input / 'annotations'
source_mapping = path_input / 'kpi_mapping'

# =============================================================================
# /PROJECT_DATA_DIR/interim
# =============================================================================
path_interim = Path('interim')
destination_pdf = path_interim / 'pdfs'
destination_annotation = r'/interim/ml/annotations/'
destination_mapping = destination_pdf = path_interim / 'kpi_mapping'
folder_text_3434 = path_interim / 'ml'
destination_extraction = folder_text_3434 / 'extraction/'
destination_curation = folder_text_3434 / 'curation'
destination_training = folder_text_3434 / 'training'


# =============================================================================
# /PROJECT_MODEL_DIR/RELEVANCE
# =============================================================================
destination_saved_models_relevance = Path(config.MODEL_DIR) / 'RELEVANCE' / 'Text' # / relevance_training_output_model_name 

# =============================================================================
# /PROJECT_MODEL_DIR/KPI_EXTRACTION
# =============================================================================
destination_saved_models_inference = Path(config.MODEL_DIR) / 'KPI_EXTRACTION' / 'Text' # / kpi_inference_training_output_model_name 

# =============================================================================
# /PROJECT_DATA_DIR/output
# =============================================================================
path_output = Path('output')
folder_relevance = path_output / 'RELEVANCE' / 'Text'
source_extraction = path_output / 'TEXT_EXTRACTION'


def project_root():
    return Path(__file__).parent