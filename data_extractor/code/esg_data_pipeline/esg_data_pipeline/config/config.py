import os
import pathlib

# General config
STAGE = "extract"    
SEED = 42

CONFIG_FOLDER = pathlib.Path(__file__).resolve().parent
ROOT = CONFIG_FOLDER.parent.parent.parent.parent
DATA_FOLDER = ROOT / "data"

#Extraction inputs
PDFTextExtractor_kwargs = {'min_paragraph_length': 30, 
                            #Set to  ANNOTATION_FOLDER if you want to extract just pdfs mentioned in the annotations
                            #Set to None to extract all pdfs in pdf folder (for production stage)
                           'annotation_folder': None,
                           'skip_extracted_files': False
                           }

#Curation inputs
TextCurator_kwargs = {
    'retrieve_paragraph': False,
    'neg_pos_ratio': 1,
    'columns_to_read': [
          'company', 'source_file', 'source_page', 'kpi_id',
          'year', 'answer', 'data_type', 'relevant_paragraphs'
      ],
    'company_to_exclude': [],
    'create_neg_samples': True,
    'min_length_neg_sample': 50,
    'seed': SEED
}

# Components
EXTRACTORS = [
    ("PDFTextExtractor", PDFTextExtractor_kwargs)
]

CURATORS = [
    ("TextCurator", TextCurator_kwargs)
]
