# ============================================================================================================================
# PDF_Analyzer
# File   : KPIResultSet.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
# ============================================================================================================================


from globals import *
from KPIMeasure import *
from ConsoleTable import *

class KPIResultSet:

	kpimeasures = None

	def __init__(self, kpimeasures = []):	
		self.kpimeasures = kpimeasures
		
	def extend(self, kpiresultset):
		self.kpimeasures.extend(kpiresultset.kpimeasures)
		
	def to_ctab(self):
		ctab = ConsoleTable(13)
		ctab.cells.append('KPI_ID')
		ctab.cells.append('KPI_NAME')
		ctab.cells.append('SRC_FILE')
		ctab.cells.append('PAGE_NUM')
		ctab.cells.append('ITEM_IDS')
		ctab.cells.append('POS_X')
		ctab.cells.append('POS_Y')
		ctab.cells.append('RAW_TXT')
		ctab.cells.append('YEAR')
		ctab.cells.append('VALUE')
		ctab.cells.append('SCORE')
		ctab.cells.append('UNIT')
		ctab.cells.append('MATCH_TYPE')
		
		for k in self.kpimeasures:
			ctab.cells.append(str(k.kpi_id  	))
			ctab.cells.append(str(k.kpi_name	))
			ctab.cells.append(str(k.src_file	))
			ctab.cells.append(str(k.page_num	))
			ctab.cells.append(str(k.item_ids	))
			ctab.cells.append(str(k.pos_x		))
			ctab.cells.append(str(k.pos_y		))
			ctab.cells.append(str(k.raw_txt		))
			ctab.cells.append(str(k.year		))
			ctab.cells.append(str(k.value		))
			ctab.cells.append(str(k.score		))
			ctab.cells.append(str(k.unit		))
			ctab.cells.append(str(k.match_type	))

		return ctab
	
	def to_string(self, max_width, min_col_width):
		ctab = self.to_ctab()
		return ctab.to_string(max_width, min_col_width)
		
		
		
	def to_json(self):
		jsonpickle.set_preferred_backend('json')
		jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
		data = jsonpickle.encode(self)
		
		return data
		
	def save_to_file(self, json_file):
		data = self.to_json()
		f = open(json_file, "w")
		f.write(data)
		f.close()
		
	def save_to_csv_file(self, csv_file):
		ctab = self.to_ctab()
		csv_str = ctab.to_string(use_format = ConsoleTable.FORMAT_CSV)

		f = open(csv_file, "w", encoding="utf-8")
		f.write(csv_str)
		f.close()
		
		
		
	@staticmethod
	def load_from_json(data):
		obj = jsonpickle.decode(data)
		return obj
		
	@staticmethod
	def load_from_file(json_file):
		f = open(json_file, "r")
		data = f.read()
		f.close()
		return KPIResultSet.load_from_json(data)		
		
		
	
	def __repr__(self):
	
		return self.to_string(120, 5)
		
		