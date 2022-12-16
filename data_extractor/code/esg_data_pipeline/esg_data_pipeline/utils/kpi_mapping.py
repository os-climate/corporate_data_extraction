import pandas as pd
from esg_data_pipeline.config import config
import os

try:
    df = pd.read_csv("/kpi_mapping.csv", header=0)
    _KPI_MAPPING = {str(i[0]): i[1] for i in df[['kpi_id', 'question']].values}
    KPI_MAPPING = {(float(key)): value for key, value in _KPI_MAPPING.items()}

    # Which questions should be added the year
    ADD_YEAR = df[df['add_year']].kpi_id.tolist()

    # Category where the answer to the question should originate from
    KPI_CATEGORY = {
        i[0]: [j.strip() for j in i[1].split(', ')] for i in df[['kpi_id', 'kpi_category']].values
    }
except Exception as e:
    KPI_MAPPING = {}
    ADD_YEAR = []
    KPI_CATEGORY = {}