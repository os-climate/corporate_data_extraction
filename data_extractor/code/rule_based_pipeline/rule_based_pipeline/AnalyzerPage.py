# ============================================================================================================================
# PDF_Analyzer
# File   : AnalyzerTable.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 AnalyzerPage refers to * AnalyzerTable (one for each HTMLTable on that page)
# Note   : 1 AnalyzerDirectory refers to * AnalyzerPage (one for each HTMLPage in that directory, resp. pdf-file)
# ============================================================================================================================


from HTMLPage import *
from AnalyzerTable import *
from AnalyzerCluster import *

class AnalyzerPage:
	htmlpage		= None
	analyzer_table 	= None
	analyzer_cluster	= None
	default_year	= None


	def __init__(self, htmlpage, default_year):
		self.htmlpage	= htmlpage
		self.analyzer_table	= []
		for t in self.htmlpage.tables:	
			self.analyzer_table.append(AnalyzerTable(t, self.htmlpage, default_year))
			sub_tabs = t.generate_sub_tables()
			for s in sub_tabs:
				self.analyzer_table.append(AnalyzerTable(s, self.htmlpage, default_year))
		
		self.analyzer_cluster = []
		#self.analyzer_cluster.append(AnalyzerCluster(htmlpage.clusters, htmlpage, default_year))
		self.analyzer_cluster.append(AnalyzerCluster(htmlpage.clusters_text, htmlpage, default_year))
		
		
		self.default_year = default_year
	
	def find_kpis(self, kpispecs):
		# find all possible occurenes of kpi on that page
		
		print_verbose(1, " ==>>>> FIND KPIS '" + kpispecs.kpi_name + "' ON PAGE: "+str(self.htmlpage.page_num) + " <<<<<=====")
		print_verbose(9, self.htmlpage)
		
		res = []
		# 1. Tables
		for a in self.analyzer_table:
			res.extend(a.find_kpis(kpispecs))
		
		# 2. Figures and Text (used for CDP reports)
		#for a in self.analyzer_cluster:
		#	res.extend(a.find_kpis(kpispecs))
		
		# 3. Regular text
		# TODO
		
		# 4. Remove dups
		res = KPIMeasure.remove_duplicates(res)
		
		#5. Adjust coords
		for k in res:
			px, py = self.htmlpage.transform_coords(k.pos_x, k.pos_y)
			k.pos_x = px
			k.pos_y = py

		
		
		return res
		