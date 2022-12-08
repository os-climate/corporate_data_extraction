# ============================================================================================================================
# PDF_Analyzer
# File   : AnalyzerTable.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 AnalyzerDirectory refers to * AnalyzerPage (one for each HTMLPage in that directory, resp. pdf-file)
# ============================================================================================================================


from AnalyzerPage import *
from HTMLDirectory import *


class AnalyzerDirectory:
	htmldirectory	= None
	analyzer_page	= None
	default_year 	= None


	def __init__(self, htmldirectory, default_year):
		self.htmldirectory	= htmldirectory
		self.analyzer_page = []
		for i in range(len(self.htmldirectory.htmlpages)):
			p = htmldirectory.htmlpages[i]
			self.analyzer_page.append(AnalyzerPage(p, default_year))
			if(config.global_analyze_multiple_pages_at_one and i < len(self.htmldirectory.htmlpages) - 1):
				p_mult = HTMLPage.merge(p, htmldirectory.htmlpages[i+1])
				self.analyzer_page.append(AnalyzerPage(p_mult, default_year))
		self.default_year = default_year
		

	"""
	TODO : Probably implementation not neccessary
	def adjust_scores_by_value_preference(self, lst, kpispecs):
		if(kpispecs.value_preference == 1.0 or len(lst) < 2):
			return lst
			
		min_val = 
		for k in lst:
			...
	"""
			
		
		
	def fix_src_name(self, kpi_measures):
		print_verbose(3, "self.htmldirectory.src_pdf_filename="+self.htmldirectory.src_pdf_filename)
		res = []
		for k in kpi_measures:
			k.set_file_path(self.htmldirectory.src_pdf_filename)
			res.append(k)
		return res
		
	
	
	def find_kpis(self, kpispecs):
		# find all possible occurenes of kpi on all pages
		
		
		res = []
		
		for a in self.analyzer_page:
			res.extend(a.find_kpis(kpispecs))
			
		if(config.global_ignore_all_years):
			res = KPIMeasure.remove_all_years(res)

		#print("\n\n\n1:"+str(res))
		
		res = KPIMeasure.remove_duplicates(res)

		#print("\n\n\n2:"+str(res))

		res = KPIMeasure.remove_bad_scores(res, kpispecs.minimum_score)		
		


		return res
	
	
	def find_multiple_kpis(self, kpispecs_lst):
		res = []
		
		for k in kpispecs_lst:
			res.extend(self.find_kpis(k))
			

		
		res = KPIMeasure.remove_bad_years(res, self.default_year)
		
		res = KPIMeasure.remove_duplicates(res)
		
		res = self.fix_src_name(res)
		
		
		
		return res