# ============================================================================================================================
# PDF_Analyzer
# File   : TestDataSample.py
# Author : Ismail Demir (G124272)
# Date   : 02.08.2020
# ============================================================================================================================

from ConsoleTable import *
from Format_Analyzer import *

class TestDataSample:

	# current format in sample csv file: 
	# Number,Sector,Unit,answer,"comments, questions",company,data_type,irrelevant_paragraphs,kpi_id,relevant_paragraphs,sector,source_file,source_page,year
	
	data_number                   = None
	data_sector                   = None
	data_unit                     = None
	data_answer                   = None
	data_comments_questions       = None
	data_company                  = None
	data_data_type                = None
	data_irrelevant_paragraphs    = None
	data_kpi_id                   = None
	data_relevant_paragraphs      = None
	data_sector                   = None
	data_source_file              = None
	data_source_page              = None
	data_year                     = None
	fixed_source_file			  = None
	
	def __init__(self):
		self.data_number 				 = 0
		self.data_sector                 = ''
		self.data_unit                   = ''
		self.data_answer                 = ''
		self.data_comments_questions     = ''
		self.data_company                = ''
		self.data_data_type              = ''
		self.data_irrelevant_paragraphs  = ''
		self.data_kpi_id                 = 0
		self.data_relevant_paragraphs    = ''
		self.data_sector                 = ''
		self.data_source_file            = ''
		self.data_source_page            = 0
		self.data_year                   = 0
		self.fixed_source_file			 = None
		
	@staticmethod
	def samples_to_string(lst, max_width=140, min_col_width=5):
		ctab = ConsoleTable(14)
		ctab.cells.append('NUMBER')
		ctab.cells.append('SECTOR')
		ctab.cells.append('UNIT')
		ctab.cells.append('ANSWER')
		ctab.cells.append('COMMENTS')
		ctab.cells.append('COMPANY')
		ctab.cells.append('DATA_TYPE')
		ctab.cells.append('IRREL_PARAG')
		ctab.cells.append('KPI_ID')
		ctab.cells.append('RELEV_PARAG')
		ctab.cells.append('SECTOR')
		ctab.cells.append('SOURCE_FILE')
		ctab.cells.append('SOURCE_PAGE')
		ctab.cells.append('YEAR')

		
		for k in lst:
			ctab.cells.append(str(k.data_number 				                       	))
			ctab.cells.append(str(k.data_sector                                       	))
			ctab.cells.append(str(k.data_unit                                         	))
			ctab.cells.append(str(k.data_answer                                       	))
			ctab.cells.append(str(k.data_comments_questions                           	))
			ctab.cells.append(str(k.data_company                                      	))
			ctab.cells.append(str(k.data_data_type                                    	))
			ctab.cells.append(str(k.data_irrelevant_paragraphs                        	))
			ctab.cells.append(str(k.data_kpi_id                                       	))
			ctab.cells.append(str(k.data_relevant_paragraphs                          	))
			ctab.cells.append(str(k.data_sector                                       	))
			ctab.cells.append(str(k.data_source_file                                  	))
			ctab.cells.append(str(k.data_source_page                                  	))
			ctab.cells.append(str(k.data_year                                         	))

		
		return ctab.to_string(max_width, min_col_width)	
	
	
	@staticmethod
	def samples_to_csv(lst):
		def escape(txt):
			txt = txt.replace("\n", "")
			txt = txt.replace("\r", "")
			txt = txt.replace('"', '""')
			return '"' + Format_Analyzer.trim_whitespaces(txt) + '"'
		
		res = ""
		for k in lst:
			res += escape(str(k.data_number 				                       	)) + ";"
			res += escape(str(k.data_sector                                       	)) + ";"
			res += escape(str(k.data_unit                                         	)) + ";"
			res += escape(str(k.data_answer                                       	)) + ";"
			res += escape(str(k.data_comments_questions                           	)) + ";"
			res += escape(str(k.data_company                                      	)) + ";"
			res += escape(str(k.data_data_type                                    	)) + ";"
			res += escape(str(k.data_irrelevant_paragraphs                        	)) + ";"
			res += escape(str(k.data_kpi_id                                       	)) + ";"
			res += escape(str(k.data_relevant_paragraphs                          	)) + ";"
			res += escape(str(k.data_sector                                       	)) + ";"
			res += escape(str(k.data_source_file                                  	)) + ";"
			res += escape(str(k.data_source_page                                  	)) + ";"
			res += escape(str(k.data_year                                         	)) + "\n"
		
		return res
		
		
	
	
	def __repr__(self):
	
		return TestDataSample.samples_to_string([self])
		