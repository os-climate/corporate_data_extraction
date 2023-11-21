import os
import pathlib

import kpi_inference_data_pipeline

# General config
SEED = 42
ROOT = pathlib.Path(kpi_inference_data_pipeline.__file__).resolve().parent
CONFIG_FOLDER = ROOT
DATA_FOLDER = ROOT
ANNOTATION_FOLDER = ROOT
EXTRACTION_FOLDER = ROOT
COLUMNS_TO_READ = [
    "company",
    "source_file",
    "source_page",
    "kpi_id",
    "year",
    "answer",
    "data_type",
    "relevant_paragraphs",
]


class CurateConfig:
    def __init__(self):
        self.val_ratio = 0
        self.seed = SEED
        self.find_new_answerable = True
        self.create_unanswerable = True


# Text KPI Inference Curator
TextKPIInferenceCurator_kwargs = {
    "annotation_folder": ANNOTATION_FOLDER,
    "agg_annotation": DATA_FOLDER / "aggregated_annotation.csv",
    "extracted_text_json_folder": EXTRACTION_FOLDER,
    "output_squad_folder": DATA_FOLDER,
    "relevant_text_path": DATA_FOLDER / "text_3434.csv",
}
