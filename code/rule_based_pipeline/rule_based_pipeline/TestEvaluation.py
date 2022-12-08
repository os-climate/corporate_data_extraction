# ============================================================================================================================
# PDF_Analyzer
# File   : TestEvaluation.py
# Author : Ismail Demir (G124272)
# Date   : 10.09.2020
# ============================================================================================================================

from TestData import *
from Format_Analyzer import *
from KPIResultSet import *
from ConsoleTable import *

class TestEvaluation:

	EVAL_TRUE_POSITIVE = 0
	EVAL_FALSE_POSITIVE = 1
	EVAL_TRUE_NEGATIVE = 2
	EVAL_FALSE_NEGATIVE = 3

	class TestEvalSample:
		kpispec = None
		kpimeasure = None
		test_sample  = None
		year = None
		pdf_file_name = None
		
		def __init__(self, kpispec, kpimeasure, test_sample, year, pdf_file_name):
			self.kpispec = kpispec
			self.kpimeasure = kpimeasure
			self.test_sample = test_sample
			self.year = year
			self.pdf_file_name = pdf_file_name
			
		def get_true_value(self):
			return None if self.test_sample is None else Format_Analyzer.to_float_number(self.test_sample.data_answer)
			
		def get_extracted_value(self):
			return None if self.kpimeasure is None else Format_Analyzer.to_float_number(self.kpimeasure.value)
			
		def eval(self):
			if(self.kpimeasure is not None and self.test_sample is not None):
				if(abs(self.get_extracted_value() - self.get_true_value()) < 0.0001):
					return TestEvaluation.EVAL_TRUE_POSITIVE
				return TestEvaluation.EVAL_FALSE_POSITIVE
				
			if(self.test_sample is not None):
				return TestEvaluation.EVAL_FALSE_NEGATIVE
				
			if(self.kpimeasure is not None):
				return TestEvaluation.EVAL_FALSE_POSITIVE
				
			return TestEvaluation.EVAL_TRUE_NEGATIVE
				
			
		def eval_to_str(self):
			eval_id = self.eval()
			if(eval_id == TestEvaluation.EVAL_TRUE_POSITIVE):
				return "True Positive"
			if(eval_id == TestEvaluation.EVAL_FALSE_POSITIVE):
				return "False Positive"
			if(eval_id == TestEvaluation.EVAL_TRUE_NEGATIVE):
				return "True Negative"
			if(eval_id == TestEvaluation.EVAL_FALSE_NEGATIVE):
				return "False Negative"
			return "Unknown"


			
	eval_samples = None
	num_true_positive = None
	num_false_positive = None
	num_true_negative = None
	num_false_negative = None
	measure_precision = None
	measure_recall = None
	
	
	def __init__(self):
		self.eval_samples = []
		self.num_true_positive = 0
		self.num_false_positive = 0
		self.num_true_negative = 0
		self.num_false_negative = 0		
		self.measure_precision = 0.0
		self.measure_recall = 0.0
		
	def do_evaluations(self):
		self.num_true_positive = 0
		self.num_false_positive = 0
		self.num_true_negative = 0
		self.num_false_negative = 0		
		for e in self.eval_samples:
			eval_id = e.eval()
			if(eval_id == TestEvaluation.EVAL_TRUE_POSITIVE):
				self.num_true_positive += 1
			if(eval_id == TestEvaluation.EVAL_FALSE_POSITIVE):
				self.num_false_positive += 1
			if(eval_id == TestEvaluation.EVAL_TRUE_NEGATIVE):
				self.num_true_negative += 1
			if(eval_id == TestEvaluation.EVAL_FALSE_NEGATIVE):
				self.num_false_negative += 1
				
		if(self.num_true_positive>0):
			self.measure_precision = self.num_true_positive / float(self.num_true_positive + self.num_false_positive)
			self.measure_recall = self.num_true_positive / float(self.num_true_positive + self.num_false_negative)
		else:
			self.measure_precision = 0.0
			self.measure_recall = 0.0	
		
	def to_string(self, max_width, min_col_width, format):
		ctab = ConsoleTable(7)
		ctab.cells.append('KPI_ID')
		ctab.cells.append('KPI_NAME')
		ctab.cells.append('PDF_FILE')
		ctab.cells.append('YEAR')
		ctab.cells.append('TRUE VALUE')
		ctab.cells.append('EXTRACTED VALUE')
		ctab.cells.append('CLASSIFICATION')
		
		for e in self.eval_samples:
			ctab.cells.append(str(e.kpispec.kpi_id))
			ctab.cells.append(str(e.kpispec.kpi_name))
			ctab.cells.append(str(e.pdf_file_name))
			ctab.cells.append(str(e.year))
			ctab.cells.append(str(e.get_true_value()))
			ctab.cells.append(str(e.get_extracted_value()))
			ctab.cells.append(e.eval_to_str().upper())

		res = ctab.to_string(max_width, min_col_width, format)
		
		res += "\nSUMMARY:\n" 
		res += "True Positives : " + str(self.num_true_positive) + "\n"
		res += "False Positives : " + str(self.num_false_positive) + "\n"
		res += "True Negatives : " + str(self.num_true_negative) + "\n"
		res += "False Negatives : " + str(self.num_false_negative) + "\n"
		res += "Precision : " + str(self.measure_precision) + "\n"
		res += "Recall : " + str(self.measure_recall) + "\n"
		
		
		return res
		
	def __repr__(self):
	
		return self.to_string(120, 5, ConsoleTable.FORMAT_CSV)		
		

	@staticmethod
	def generate_evaluation(kpispecs, kpiresults, test_data):
		pdf_file_names = test_data.get_fixed_pdf_list()
		
		res = TestEvaluation()

		for kpispec in kpispecs:
			print_verbose(1, 'Evaluating KPI: kpi_id='  +str(kpispec.kpi_id) + ', kpi_name="' + kpispec.kpi_name + '"')
			for pdf_file_name in pdf_file_names:
				print_verbose(1, '--->> Evaluating PDF = "' + pdf_file_name + '"')
				# Find values in test data samples for this kpi/pdf:
				for s in test_data.samples:
					if(s.data_kpi_id == kpispec.kpi_id and s.fixed_source_file == pdf_file_name):
						#match (True KPI exists in pdf)
						cur_eval_sample = None
						#are there any matches in our results?
						for k in kpiresults.kpimeasures:
							if(k.kpi_id == kpispec.kpi_id and k.src_file == pdf_file_name and k.year == s.data_year):
								#yes (Extracted KPI exists)
								cur_eval_sample = TestEvaluation.TestEvalSample(kpispec, k, s, k.year, pdf_file_name)
								break
						if(cur_eval_sample is None):
							#no
							cur_eval_sample = TestEvaluation.TestEvalSample(kpispec, None, s, s.data_year, pdf_file_name)
						res.eval_samples.append(cur_eval_sample)
							
				# Any unmatched kpi results (ie. extracted KPIs) left?
				for k in kpiresults.kpimeasures:
					if(k.src_file != pdf_file_name):
						#print('skip: ' +str(k))
						continue
					found = False
					for e in res.eval_samples:
						if(e.kpimeasure is not None and k.kpi_id == e.kpispec.kpi_id and k.year == e.year and e.kpimeasure.src_file == pdf_file_name):
							found = True
							break
					if(not found):
						#unmatched
						cur_eval_sample = TestEvaluation.TestEvalSample(kpispec, k, None, k.year, pdf_file_name)
						res.eval_samples.append(cur_eval_sample)
						
		res.do_evaluations()
		return res
					
				
								
					
				
				
				