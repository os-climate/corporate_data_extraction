import pandas as pd
from model_pipeline.config_farm_train import Config
import os
from pathlib import Path

# config = Config()

# df = pd.read_csv(Path(config.root).parent.parent / "kpi_mapping.csv", header=0)
try:
    df = pd.read_csv("/app/code/kpi_mapping.csv", header=0)
    _KPI_MAPPING = {
        str(i[0]): (i[1], [j.strip() for j in i[2].split(",")]) for i in df[["kpi_id", "question", "sectors"]].values
    }
    KPI_MAPPING = {(float(key)): value for key, value in _KPI_MAPPING.items()}

    # Category where the answer to the question should originate from
    KPI_CATEGORY = {i[0]: [j.strip() for j in i[1].split(", ")] for i in df[["kpi_id", "kpi_category"]].values}

    KPI_SECTORS = list(set(df["sectors"].values))
except:
    KPI_MAPPING = {}
    KPI_CATEGORY = {}
    KPI_SECTORS = []
