# ============================================================================================================================
# PDF_Analyzer
# File   : KPIMeasure.py
# Author : Ismail Demir (G124272)
# Date   : 19.06.2020
# ============================================================================================================================


from globals import *
from Format_Analyzer import *

class KPIMeasure:
	kpi_id		= None
	kpi_name	= None
	src_file	= None
	src_path	= None
	company_name	= None
	page_num	= None
	item_ids	= None
	pos_x		= None
	pos_y		= None
	raw_txt		= None
	year		= None
	value		= None
	score		= None
	unit		= None
	match_type	= None
	tmp			= None # for temporary values used by an Analyzer
	
	
	def __init__(self):
		self.kpi_id   = -1
		self.kpi_name = ''
		self.src_file = ''
		self.src_path = ''
		self.company_name = ''
		self.page_num = -1
		self.item_ids = []
		self.pos_x	  = -1
		self.pos_y	  = -1
		self.raw_txt  = ''
		self.year	  = -1
		self.value	  = ''
		self.score	  = -1
		self.unit	  = ''
		self.match_type = '' 
		self.tmp = None
		
	def set_file_path(self, file_path):
		fp = file_path.replace('\\', '/')
		self.src_file = Format_Analyzer.extract_file_name(fp)
		self.src_path = remove_trailing_slash(Format_Analyzer.extract_file_path(fp)[0])
		self.company_name = self.src_path[self.src_path.rfind('/')+1:]
		
	def __repr__(self):
		return "<KPIMeasure: id=" +str(self.kpi_id)+",name="+str(self.kpi_name)+", "+str(self.src_file)+", page_num="+str(self.page_num)+", id="+str(self.item_ids)+", x/y=" \
		   +str(self.pos_x)+", "+str(self.pos_y)+", raw="+str(self.raw_txt)+", match_type="+str(self.match_type) \
		   +", unit="+str(self.unit)+", YEAR="+str(self.year)+", VALUE="+str(self.value)+", SCORE="+str(self.score)+">"
		   
		   
		   
	@staticmethod
	def remove_all_years(lst):
		res = []
		for it in lst:
			it.year=-1
			res.append(it)
		return res
	
	@staticmethod
	def remove_duplicates(lst): # from the list of KPIMeasure "lst", remove all duplicates (same kpi_name and year), with less than best score
	
		#return lst # Dont remoe anything (for debug purposes only)
	
		keep = [False] * len(lst)
		for i in range(len(lst)):
			better_kpi_exists = False
			for j in range(len(lst)):
				if(i==j):
					continue
				if(lst[j].kpi_name == lst[i].kpi_name and lst[j].year == lst[i].year and (lst[j].score > lst[i].score or (lst[j].score == lst[i].score and j > i ))):
					better_kpi_exists = True
					break
			keep[i] = not better_kpi_exists
		
		res = []
		for i in range(len(lst)):
			if(keep[i]):
				res.append(lst[i])
		
		return res

	@staticmethod
	def remove_bad_scores(lst, minimum_score):


		#return lst # Dont remoe anything (for debug purposes only)
	
		res = []
		
		max_score = {}
		
		for k in lst:
			max_score[k.kpi_name] = k.score if not k.kpi_name in max_score else max(k.score, max_score[k.kpi_name])
		
		for k in lst:
			if(k.score >= minimum_score and k.score >= max_score[k.kpi_name] * 0.75 ):
				res.append(k)
		
		return res
		
	@staticmethod
	def remove_bad_years(lst, default_year):
		
		
		# do we have entries with a year?
		year_exist = []
		
		for k in lst:
			if(k.year != -1):
				year_exist.append(k.kpi_name)
				break
		
		
		res = []
		year_exist = list(set(year_exist))
		

		
		for k in lst:
			if(k.year == -1):
				if(not k.kpi_name in year_exist):
					k.year = default_year
					res.append(k)
				
			else:
				res.append(k)
		
		return res














