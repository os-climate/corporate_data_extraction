# ============================================================================================================================
# PDF_Analyzer
# File   : AnalyzerTable.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 AnalyzerPage refers to * AnalyzerTable (one for each HTMLTable on that page)
# ============================================================================================================================


from HTMLTable import *
from HTMLPage import *
from KPISpecs import *
from KPIMeasure import *

HIERARCHY_DIR_UP = 0
HIERARCHY_DIR_LEFT = 1

DIR_UPWARDS = -1
DIR_DOWNWARDS = 1


class AnalyzerTable:

	class YearRow: # a row that is assumed to be a headline with years
		row_num	= None
		years 	= None #  a mapping: year -> row, col
	
		def __init__(self, row_num, years):
			self.row_num 	= row_num
			self.years		= years
		
		def __repr__(self):
			return '<row_num='+str(self.row_num)+', years='+str(self.years)+'>'
		
		

	htmltable 	= None
	htmlpage	= None
	items		= None
	default_year	= None
	
	table_hierarchy	= None # for each ix, a refernece to the parent ix (or -1, if root)
	year_rows		= None # all rows containing years, each will be a YearRow
	

	def get_num_cols(self):
		return self.htmltable.num_cols
		
	def get_num_rows(self):
		return self.htmltable.num_rows
		
	def get_ix(self, i, j):
		return self.htmltable.get_ix(i, j)
		
	def get_row_and_col_by_ix(self, ix):
		return self.htmltable.get_row_and_col_by_ix(ix)

	def has_item_at_ix(self, i): # i=ix
		return self.htmltable.has_item_at_ix(i)
		
	def has_item_at(self, i, j): # i=row, j=col
		return self.htmltable.has_item_at(i, j)
		
	def get_item(self, i, j):
		return self.htmltable.get_item(i, j)
		
	def get_item_by_ix(self, ix):
		return self.htmltable.get_item_by_ix(ix)
		
	def find_next_non_empty_cell_return_row_only(self, i, j, dir):
		while(i>0 and i<self.get_num_rows()-1):
			i += dir
			if(self.has_item_at(i, j)):
				return i
		return -1 # not found
				
		
	def get_depth(self, i, j, dir):
		ident_threshold = (3.0 / 609.0) * self.htmlpage.page_width if dir==HIERARCHY_DIR_UP else (3.0 / 609.0) * self.htmlpage.page_height
		
		if(not self.has_item_at(i, j)):
			return 999999999
		it = self.get_item(i, j)
		if(dir==HIERARCHY_DIR_UP):
			return it.get_depth() + ((int)( it.pos_x / ident_threshold )   * 10000 if it.alignment == ALIGN_LEFT else 0)
		return it.get_depth() + ((int)(it.pos_y / ident_threshold) * 10000 if it.alignment == ALIGN_LEFT else 0)
			
		
	def find_next_parent_cell(self, r0, c0, dir): #row=r0, col=c0
		#print("------------>> find_next_parent_cell: "+ str(r0) + ',' + str(c0) ) 
		d0 = self.get_depth(r0, c0, dir)
		if(d0 == 999999999):
			return -1 # empty cell
			
		if(dir==HIERARCHY_DIR_UP):
			for i in range(r0 - 1, -1, -1):
				d = self.get_depth(i, c0, dir)
				if(d < d0):
					#print("---------------->> " + str(i) + "," + str(c0)) 
					return self.get_ix(i, c0)
		elif(dir==HIERARCHY_DIR_LEFT):
			for j in range(c0 - 1, -1, -1):
				d = self.get_depth(r0, j, dir)
				if(d < d0):
					return self.get_ix(r0, j)
					
		#print("---------------->> root")
		return -1 # not found / root



	def calculate_hierarchy(self, dir):
		for i in range(self.get_num_rows()):
			for j in range(self.get_num_cols()):
				self.table_hierarchy[dir][self.get_ix(i,j)] = self.find_next_parent_cell(i, j, dir)
				
				
	def get_aligned_multirow_txt_with_rect(self, r0, c0):
		def go(dir, init_depth):
			res = []
			rect = Rect(9999999, 9999999, -1, -1)
			r = r0 + dir
			while(r > 0 and r < self.get_num_rows()):
				if(not self.has_item_at(r, c0)):
					break # nothing here (TODO: maybe just skip these?)
				if(self.get_depth(r, c0, HIERARCHY_DIR_UP) != init_depth):
					break # other depth => unrelated
				# do we have other numeric values in that row?
				has_num_values = False
				for j in range(self.get_num_cols()):
					if(j==c0):
						continue
					if(self.has_item_at(r, j) and Format_Analyzer.looks_weak_numeric(self.get_item(r, j).txt)):
						has_num_values = True
						break
				if(has_num_values):
					break
				res.append(self.get_item(r, c0).txt)
				rect.grow(self.get_item(r, c0).get_rect())
				r += dir
			return res, rect
				
				
				
		
		#sometimes a cell contains of multiple rows. we want to match the whole cell,
		#but to avoid overmatching, we make sure that in such cases in no other connected row
		#any values can be stored
		
		res = []
		rect = Rect(9999999, 9999999, -1, -1)
		
		if(not self.has_item_at(r0, c0)):
			return res, rect
			
		res.append(self.get_item(r0, c0).txt )
		rect.grow(self.get_item(r0, c0).get_rect())
		
		init_depth = self.get_depth(r0, c0, HIERARCHY_DIR_UP)
		
		res_up, rect_up = go(DIR_UPWARDS, init_depth)
		res_down, rect_down = go(DIR_DOWNWARDS, init_depth)
		
		for i in range(max(len(res_up),len(res_down))):
			if(i<len(res_up)):
				res.append(res_up[i])
			if(i<len(res_down)):
				res.append(res_down[i])
		rect.grow(rect_up)
		rect.grow(rect_down)
		
		return res, rect
				
		
		
		
		
		
		
		
		
	def get_txt_nodes(self, r0, c0, dir, include_special_items):
		res = []
		ix = self.get_ix(r0, c0)
		rect = Rect(9999999, 9999999, -1, -1)
		while(self.has_item_at_ix(ix)):
			r, c = self.get_row_and_col_by_ix(ix)
			cur_res, cur_rect = self.get_aligned_multirow_txt_with_rect(r, c)
			rect.grow(cur_rect)
			res.extend(cur_res)
			
			#rect.grow(self.get_item_by_ix(ix).get_rect())
			#res.append(self.get_item_by_ix(ix).txt)
			ix = self.table_hierarchy[dir][ix]
			


		if(include_special_items):
			sp_idx = self.htmltable.find_special_item_idx_in_rect(rect)
			for i in sp_idx:
				res.append(self.items[i].txt)
		return res
		
	def get_txt_nodes_above(self, r0, c0, include_special_items, break_at_number):
		# search for text items that are above the current cell
		res = []
		r = r0 
		while(r > 0):
			r -= 1
			if(not self.has_item_at(r, c0)):
				continue # empty
			txt = self.get_item(r, c0).txt
			if(Format_Analyzer.looks_weak_non_numeric(txt)):
				res.append(txt)
			else:
				if(break_at_number):
					break #a number or soemthing that is no text	
			

		if(include_special_items and self.has_item_at(r0, c0)):
			rect = self.get_item(r0, c0).get_rect()
			rect.y0 = 0
			sp_idx = self.htmltable.find_special_item_idx_in_rect(rect)
			for i in sp_idx:
				res.append(self.items[i].txt)
		return res
	
		
	def get_txt_headline(self):
		res = []
		for h_idx in self.htmltable.headline_idx:
			res.append(self.items[h_idx].txt)
		return res
		
	def get_first_non_empty_row(self, r0, c0): #typically, set r0 = 0 to search from top. If no such row found, then "num_rows" is returned
		r = r0
		while(r < self.get_num_rows()):
			if(self.has_item_at(r, c0)):
				break
			r +=1
		return r

			
	def get_multi_row_headline(self, r0, c0, include_special_items):
		# get first non-empty row
		r = self.get_first_non_empty_row(r0, c0)
		if(r == self.get_num_rows() or not Format_Analyzer.looks_weak_words(self.get_item(r, c0))):
			return ''


		res = ''
		# special items?
		if(include_special_items):
			rect = self.get_item(r, c0).get_rect()
			rect.y0 = 0
			sp_idx = self.htmltable.find_special_item_idx_in_rect(rect)
			res += HTMLItem.concat_txt(htmlpage.unfold_idx_to_items(sp_idx))
		
		# start at r,c0
		font = self.get_item(r, c0).get_font_characteristics()
		max_row_spacing = self.get_item(r, c0).font_size * 1.5
		res += self.get_item(r, c0).txt
		last_y1 = self.get_item(r, c0).get_rect().y1

		while(r < self.get_num_rows() - 1):
			r += 1
			if(not self.has_item_at(r, c0)):
				continue
			cur_font = self.get_item(r, c0).get_font_characteristics()
			if(cur_font != font):
				break # different font => break here
			cur_rect = self.get_item(r, c0).get_rect()
			if(cur_rect.y0 > last_y1 + max_row_spacing):
				break # rows are too far apart => break here
			txt = self.get_item(r, c0).txt
			if(not Format_Analyzer.looks_weak_words(txt)):
				break # not a text anymore => break here
			res += ' ' + txt
			
			
			
		return res

		
	def row_looks_like_year_line(self, r0): #at least one column is a year? if yes, an dict with year -> row_num, col_num is returned. If not, None
		num_years = 0
		res = {}
		for j in range(self.get_num_cols()):
			if(self.has_item_at(r0, j)):
				txt = self.get_item(r0, j).txt
				if(Format_Analyzer.looks_year(txt)):
					num_years +=1
					y = Format_Analyzer.to_year(self.get_item(r0, j).txt)
					if(y not in res):
						res[y] = (r0, j)
				elif(Format_Analyzer.looks_numeric(txt)):
					# some other number occured => this is probably not a line of years
					return None
				
		return res if num_years >= 1 else None
		
		
	"""
	old / not used anymore
	def is_table_with_years_at_top(self): #do we have a top row with years? if yes, a dict with year -> row_num, col_num is returned. If not, None
		for j in range(self.get_num_cols()):
			i = self.get_first_non_empty_row(0, j)
			if(i == self.get_num_rows()):
				continue # col is completely empty
			if(Format_Analyzer.looks_year(self.get_item(i,j).txt)):
				years = self.row_looks_like_year_line(i)
				if(years is not None):
					return years
					
		return None
	"""
	
	def find_all_year_rows(self):
		self.year_rows = []
		for i in range(self.get_num_rows()):
			years = self.row_looks_like_year_line(i)
			if(years is not None):
				self.year_rows.append(AnalyzerTable.YearRow(i, years))
				
				
	def find_applicable_year_line(self, r0):
		first_match = None
		for i in range(len(self.year_rows)-1, -1, -1):
			if(self.year_rows[i].row_num <= r0):
				first_match = self.year_rows[i]#.years
				break
				
		# now we look for a better match (that contain more year values)
		if(first_match is not None):
			
			best_match = first_match

			for i in range(len(self.year_rows)-1, -1, -1):
				if(self.year_rows[i].row_num < first_match.row_num and self.year_rows[i].row_num >=  first_match.row_num - 7): #max 7 lines above
					if(len(self.year_rows[i].years) > len(best_match.years)):
						best_match = self.year_rows[i]
			
			return best_match.years
		
		
		return None
				
		
	def find_applicable_items_for_table_with_years(self, r0):
		def return_items_for_row(r, years):
			if(years is None or len(years) == 0):
				return None
				
			res = {}
			for y, cell in years.items():
				if(cell[0] != r): # never match items that are in same row as the year numbers
					res[y] = self.get_item(r, cell[1])
			return res
		
		def contains_items(d): # check if dict d contains some items at all
			for y, it in d.items():
				if(it is not None):
					return True
			return False
			
		def advance_row(init_depth, r1):
			r = r1 + 1
			while(r < self.get_num_rows()):
				if(not self.has_item_at(r, 0)):
					return r
				if(self.get_depth(r, 0, HIERARCHY_DIR_UP) <= init_depth):
					break# another left item was found at same depth => stop process
				r  += 1
			return self.get_num_rows() #nothing found
		
		r = r0
		init_depth = self.get_depth(r0, 0, HIERARCHY_DIR_UP)
		while(r < self.get_num_rows()):
			cur_years = self.find_applicable_year_line(r)
			print_verbose(8, '.........-> r='+str(r)+', cur_years='+str(cur_years))
			cur_items = return_items_for_row(r, cur_years)
			if(cur_items is not None and contains_items(cur_items)):
				#we found the applicable items
				return r, cur_items
			#advace to next row
			r = advance_row(init_depth, r)
		return self.get_num_rows(), None
			
			
	def find_applicable_row_with_items_for_any_left_oriented_table(self, r0):
		
		def contains_items(r): # check if dict d contains some items at all
			for j in range(self.get_num_cols()):
				if(self.has_item_at(r, j) and Format_Analyzer.looks_numeric(self.get_item(r, j).txt)):
					return True
			return False
			
		def advance_row(init_depth, r1):
			r = r1 + 1
			while(r < self.get_num_rows()):
				if(not self.has_item_at(r, 0)):
					return r
				if(self.get_depth(r, 0, HIERARCHY_DIR_UP) <= init_depth):
					break# another left item was found at same depth => stop process
				r  += 1
			return self.get_num_rows() #nothing found
		
		r = r0
		init_depth = self.get_depth(r0, 0, HIERARCHY_DIR_UP)
		while(r < self.get_num_rows()):
			if(contains_items(r)):
				#we found the applicable items
				return r
			#advance to next row
			r = advance_row(init_depth, r)
		return None
				
	def find_applicable_unit_item(self, kpispecs, r0):
		# returns the applicable item that contains the corresponding unit
		sp_item = self.htmltable.find_applying_special_item(r0)
		print_verbose(7, '....unit_item->sp_item='+str(sp_item))
		if(sp_item is not None and kpispecs.match_unit(sp_item.txt)):
			return sp_item.txt
		
		# look for other unit items 
		search_rect = self.htmltable.rows[r0]
		search_rect.y0 =  0 #self.htmltable.table_rect.y0 - self.htmlpage.page_height * 0.125
		items_idx = self.htmlpage.find_items_within_rect(search_rect, [CAT_HEADLINE, CAT_OTHER_TEXT, CAT_TABLE_DATA, CAT_TABLE_HEADLINE, CAT_TABLE_SPECIAL, CAT_MISC, CAT_FOOTER])
		match_idx = -1
		for i in items_idx:
			txt = self.htmlpage.explode_item(i)
			print_verbose(10,'.......trying instead: ' + txt)
			if(kpispecs.match_unit(txt)):
				print_verbose(10,'...........===> match!') 
				if(match_idx == -1 or self.items[i].pos_y > self.items[match_idx].pos_y):
					print_verbose(10,'...........===> better then previous match. new match_idx='+str(i)) 
					match_idx = i
		if(match_idx != -1):
			return self.htmlpage.explode_item(match_idx)
		
		return None
			
		
	def search_year_agressive(self, search_rect, min_year, max_year, base_pos_x, base_pos_y, aggressive_year_pattern):
		items_idx = self.htmlpage.find_items_within_rect(search_rect, [CAT_HEADLINE, CAT_OTHER_TEXT, CAT_TABLE_DATA, CAT_TABLE_HEADLINE, CAT_TABLE_SPECIAL, CAT_MISC, CAT_FOOTER])
		best_year = -1
		best_dist = 9999999
		for i in items_idx:
			it = self.items[i]
			cur_x, cur_y = it.get_rect().get_center()
			dist_x = abs(cur_x - base_pos_x)
			dist_y = abs(cur_y - base_pos_y)
			if(cur_x > base_pos_x):
				dist_x *= 3.0 #prefer items to the left
			dist_1 = min(dist_x, dist_y)
			dist_2 = max(dist_x, dist_y) / 3.0 # prefer ortoghonally aligned items
			cur_dist = (dist_1*dist_1 + dist_2*dist_2)**0.5
			if(cur_dist < best_dist):
				for w in it.words:
					cur_year = None
					if(not aggressive_year_pattern):
						if(Format_Analyzer.looks_year(w.txt)):
							cur_year = Format_Analyzer.to_year(w.txt) #by Lei
							#cur_year = int(w.txt)
					else:
						cur_year = Format_Analyzer.looks_year_extended(w.txt)
					print_verbose(11, '..................... Analyzing possible year string: "'+w.txt+'" => ' +str(cur_year))
						
					if(cur_year is not None and cur_year >= min_year and cur_year <= max_year):
						best_year = cur_year
						best_dist = cur_dist

		return best_year




	def find_kpi_with_direct_years(self, kpispecs, bonus): 
		# find KPIs that are directly aligned with year headline
		# Example:
		#                     2019     2018    2017
		#  Hydrocarbons        123      456     789
		#
		#  ==> Result: 2019: 123 ; 2018: 456; 2017: 789
		
		
		if(self.year_rows is None or len(self.year_rows) == 0):
			return [] # invalid table for this search
			
			
		# base score from headlines:
		print_verbose(5,  '<<< ================================= >>>')
		print_verbose(5,  '<<== FIND_KPI_WITH_DIRECT_YEARS ==>>')
		print_verbose(5,  '<<< ================================= >>>')
		print_verbose(5,  ' ')

		print_verbose(5,  'year_rows = ' + str(self.year_rows))
		
		print_verbose(5,  'Looking at headlines')
		h_txt_nodes = self.get_txt_headline()
		h_match_dummy, h_score = kpispecs.match_nodes(h_txt_nodes) 
		h_score *= 0.5 #decay factor for headline
		print_verbose(5,  'Headline: ' + str(h_txt_nodes)+ ', score=' + str(h_score))

		if(h_score < 0):
			return [] # headline contains something that must be excluded
		
			
			
		# normal score from acutal items:
		res = []
		
		previous_txt_node_with_no_values = ''
		
	
		for i in range(self.get_num_rows()):
			txt_nodes = self.get_txt_nodes(i, 0, HIERARCHY_DIR_UP, True)
			txt_nodes = txt_nodes + ([previous_txt_node_with_no_values] if previous_txt_node_with_no_values != '' and previous_txt_node_with_no_values not in txt_nodes else [])
			print_verbose(5, 'Looking at row i='+str(i)+', txt_nodes='+str(txt_nodes))
			txt_match, score = kpispecs.match_nodes(txt_nodes)
			print_verbose(5, '---> score='+str(score))
			if(not txt_match):
				print_verbose(5, '---> No match')
				continue #no match
			value_row, value_items = self.find_applicable_items_for_table_with_years(i)
			if(value_items is None):
				print_verbose(5, '---> No values found')
				if(self.has_item_at(i, 0)):
					previous_txt_node_with_no_values = self.get_item(i, 0).txt
				else:
					previous_txt_node_with_no_values = '' 
				continue #no values found
			missmatch_value = False
			print_verbose(6, '-------> value_row / value_items= '+str(value_row)+' / '+str(value_items))
			for y, it in value_items.items():
				if(it is None):
					continue
				if(not kpispecs.match_value(it.txt)):
					missmatch_value = True
					break
			if(missmatch_value):
				print_verbose(5, '---> Value missmatch')
				continue # value missmatch
			txt_unit = self.find_applicable_unit_item(kpispecs, value_row)
			if(txt_unit is None):
				print_verbose(5, '---> Unit not matched')
				continue #unit not matched

			# determine score multiplier 
			multiplier = 1.0
			
			for y, it in value_items.items():
				if(it is None):
					continue				
				multiplier *= 1.2
			
			if(multiplier > 1.0):
				multiplier /= 1.2 # we counted one item too much, so divide once
			
			for y, it in value_items.items():
				if(it is None):
					continue

				anywhere_match, anywhere_match_score = kpispecs.match_anywhere_on_page(self.htmlpage, it.this_id)
				if(not anywhere_match):
					print_verbose(5, '---> anywhere-match was not matched on this page. No other match possible.')
					return []
					
				total_score =  score + h_score + anywhere_match_score + bonus
				if(total_score < kpispecs.minimum_score):
					print_verbose(5, '---> Total score '+str(total_score)+' is less than min. score '+str(kpispecs.minimum_score))
					continue
					
					
				kpi_measure = KPIMeasure()
				kpi_measure.kpi_id   = kpispecs.kpi_id
				kpi_measure.kpi_name = kpispecs.kpi_name
				kpi_measure.src_file = 'TODO'
				kpi_measure.page_num = self.htmlpage.page_num
				kpi_measure.item_ids = [it.this_id]
				kpi_measure.pos_x	  = it.pos_x
				kpi_measure.pos_y	  = it.pos_y
				kpi_measure.raw_txt  = it.txt
				kpi_measure.year	  = y
				kpi_measure.value	  = kpispecs.extract_value(it.txt)			
				kpi_measure.score	  = total_score * multiplier
				kpi_measure.unit	  = txt_unit
				kpi_measure.match_type= 'AT.direct'
				res.append(kpi_measure)
				print_verbose(4, '---> Match: ' + str(kpi_measure) + ': score='+str(score)+',h_score='+str(h_score)+',anywhere_match_score='+str(anywhere_match_score)+',bonus='+str(bonus)+', multiplier='+str(multiplier))
				
		res = KPIMeasure.remove_duplicates(res)
		return res
				
	
	
	
	def find_kpi_with_indirect_years(self, kpispecs, bonus): 
		# find KPIs that are only indirectly connected with year headline, or not at all
		# Example:
		#  Year                                         2019                           
		#                     Upstream    Downstream   Total
		#  Sales:                    1             2       3
		#
		#  ==> Result (for KPI "Downstream Sales"): 2019: 2
		
		
			
		# base score from headlines:
		print_verbose(5,  '<<< ================================= >>>')
		print_verbose(5,  '<<== FIND_KPI_WITH_INDIRECT_YEARS ==>>')
		print_verbose(5,  '<<< ================================= >>>')
		print_verbose(5,  ' ')

		print_verbose(5,  'Looking at headlines')
		h_txt_nodes = self.get_txt_headline()
		h_match_dummy, h_score = kpispecs.match_nodes(h_txt_nodes) 
		if(h_score < 0):
			return [] # headline contains something that must be excluded
		
		
		h_score *= 0.1 #decay factor for headline
		print_verbose(5,  'Headline: ' + str(h_txt_nodes)+ ', score=' + str(h_score))
			
			
			
		# normal score from acutal items:
		res = []


		# find possible fixed left columns
		fixed_left_cols = [0]
		for j in range(1, self.get_num_cols()):
			if(self.htmltable.col_looks_like_text_col(j)):
				fixed_left_cols.append(j)
		
		print_verbose(6, 'fixed_left_cols='+str(fixed_left_cols))

		for fixed_left_column in fixed_left_cols:
			#fixed_left_column = 6
			for i in range(self.get_num_rows()):
				txt_nodes_row = self.get_txt_nodes(i, fixed_left_column, HIERARCHY_DIR_UP, True)
				font_size_row_node = None
				if(self.has_item_at(i, fixed_left_column)):
					font_size_row_node = self.get_item(i, fixed_left_column).font_size
					
				print_verbose(5, 'Looking at row i='+str(i)+', txt_nodes_row='+str(txt_nodes_row)+',fonz_size='+str(font_size_row_node))

				value_row = self.find_applicable_row_with_items_for_any_left_oriented_table(i)

				if(value_row is None):
					print_verbose(5, '---> No values found')
					continue #no values found
					
				txt_unit = self.find_applicable_unit_item(kpispecs, value_row)
				
				print_verbose(6, '-------> txt_unit='+str(txt_unit))
				
				if(txt_unit is None):
					print_verbose(5, '---> Unit not matched')
					continue #unit not matched		

				years = self.find_applicable_year_line(i)
				
				print_verbose(5, '--> years= '+str(years))
				for j in range(fixed_left_column + 1, self.get_num_cols()):
					if(not self.has_item_at(value_row, j)):
						continue # empty cell
						
					it = self.get_item(value_row, j)
					value_txt = it.txt
					font_size_cell = it.font_size
					print_verbose(5, '\n-> Looking at cell: row,col=' + str(value_row) +',' + str(j)+':' + str(value_txt) + ', font_size=' +str(font_size_cell))
					if(font_size_row_node is not None and (font_size_cell < font_size_row_node / 1.75 or font_size_cell > font_size_row_node * 1.75)):
						print_verbose(5, '---> Fontsize missmatch')
						continue # value missmatch
					if(not kpispecs.match_value(value_txt)):
						print_verbose(5, '---> Value missmatch')
						continue # value missmatch
						
					txt_nodes_col = self.get_txt_nodes_above(value_row, j, True, False) # TODO: Really use False here? 
					print_verbose(5, '---> txt_nodes_col='+str(txt_nodes_col))
					print_verbose(6, '......... matching against: ' + str(txt_nodes_row + txt_nodes_col))
					txt_match, score = kpispecs.match_nodes(txt_nodes_row + txt_nodes_col)
					print_verbose(5, '---> score='+str(score))
					if(not txt_match):
						print_verbose(5, '---> No match')
						continue #no match
						
					# find best year match
					kpi_year = -1
					bad_year_match = False
					if(years is not None):
						min_diff = 9999999
						for y, cell in years.items():
							cur_diff = abs(cell[1] - j)
							if(cur_diff < min_diff):
								min_diff = cur_diff
								kpi_year = Format_Analyzer.to_year(self.get_item(cell[0], cell[1]).txt) #by Lei
							if(cell[0]==i and cell[1]==j):
								# we matched the year as value itself => must be wrong
								bad_year_match = True
					
					if(bad_year_match):
						print_verbose(5, '-----> Bad year match: year is same as value')
						continue
						
					# if still no year found, then search more
					if(kpi_year == -1):
						print_verbose(7, '......---> no year found. searching more agressively')
						search_rect = self.htmltable.table_rect
						search_rect.y1 = it.pos_y
						next_non_empty_row = self.find_next_non_empty_cell_return_row_only(value_row, j, DIR_DOWNWARDS)
						max_add = 999999 # we also want to to look a LITTLE bit downwards, in case of two-line-description cells that refer to this cell
						if(next_non_empty_row != -1):
							max_add = (self.get_item(next_non_empty_row, j).pos_y - (it.pos_y + it.height)) * 0.8
						
						search_rect.y1 += min(it.height * 1.0, max_add)
						print_verbose(8, '..............-> max_add='+str(max_add)+ ', y1(old)=' +str(it.pos_y) + ', y1(new)=' + str(search_rect.y1) )
						base_pos_x, base_pos_y = it.get_rect().get_center()
						kpi_year = self.search_year_agressive(search_rect, self.default_year - 10, self.default_year, base_pos_x, base_pos_y, aggressive_year_pattern = False)
						if(kpi_year == -1):
							print_verbose(7, '........---> still no year found. searching even more agressively')
							kpi_year = self.search_year_agressive(search_rect, self.default_year - 10, self.default_year, base_pos_x, base_pos_y, aggressive_year_pattern = True)
						if(kpi_year == -1):
							print_verbose(7, '........---> still no year found. searching even MORE agressively')
							search_rect.y0 = 0
							search_rect.x0 = 0
							search_rect.x1 = 9999999
							kpi_year = self.search_year_agressive(search_rect, self.default_year - 10, self.default_year, base_pos_x, base_pos_y, aggressive_year_pattern = True)
						print_verbose(7, '.........-> year found='+str(kpi_year) if kpi_year != -1 else '..........-> still nothing found. give up.')
					
					
					anywhere_match, anywhere_match_score = kpispecs.match_anywhere_on_page(self.htmlpage, it.this_id)
					if(not anywhere_match):
						print_verbose(5, '---> anywhere-match was not matched on this page. No other match possible.')
						return []
						
					total_score = score + h_score + anywhere_match_score + bonus
					
					if(total_score < kpispecs.minimum_score):
						print_verbose(5, '---> Total score '+str(total_score)+' is less than min. score '+str(kpispecs.minimum_score))
						continue
						
					kpi_measure = KPIMeasure()
					kpi_measure.kpi_id   = kpispecs.kpi_id
					kpi_measure.kpi_name = kpispecs.kpi_name
					kpi_measure.src_file = 'TODO'
					kpi_measure.page_num = self.htmlpage.page_num
					kpi_measure.item_ids  = [it.this_id]
					kpi_measure.pos_x	  = it.pos_x
					kpi_measure.pos_y	  = it.pos_y
					kpi_measure.raw_txt  = it.txt
					kpi_measure.year	  = kpi_year if kpi_year != -1 else self.default_year
					kpi_measure.value	  = kpispecs.extract_value(it.txt)			
					kpi_measure.score	  = total_score
					kpi_measure.unit	  = txt_unit
					kpi_measure.match_type= 'AT.indirect'
					kpi_measure.tmp		= i # we use this to determine score multiplier
					res.append(kpi_measure)
					print_verbose(4, '---> Match: ' + str(kpi_measure))
				
		res = KPIMeasure.remove_duplicates(res)
		
		
		row_multiplier = {}
		row_years_taken = {}
		for kpi in res:
			row = kpi.tmp
			if(row in row_multiplier):
				if(kpi.year not in row_years_taken[row]):
					row_multiplier[row] *= 1.2
					row_years_taken[row].append(kpi.year)
			else:
				row_multiplier[row] = 1.0
				row_years_taken[row] = [kpi.year]
		
		for kpi in res:
			kpi.score *= row_multiplier[kpi.tmp]
			
		
		print_verbose(5, "===> found AT.indirect KPIs on Page " + str(self.htmlpage.page_num) + ": " + str(res) + "\n================================")
		
		return res
				
	
	
	
			
					
	def find_kpis(self, kpispecs):
		# Find all possible occurences of KPIs in that table
		print_verbose(6, "Analyzing Table :\n" +str(self.htmltable))
		res = []
		res.extend(self.find_kpi_with_direct_years(kpispecs, 100)) # with years
		res.extend(self.find_kpi_with_indirect_years(kpispecs, 0)) # without years
		
		
		# ... add others here
		
		res = KPIMeasure.remove_duplicates(res)
		
		if(len(res) > 0):
			print_verbose(2, "Found KPIs on Page " + str(self.htmlpage.page_num) +",  Table : \n" +str(self.htmltable.get_printed_repr()) + "\n" + str(res) + "\n================================")
		
		return res
				
			
				
		
		
		
		
		
	def __init__(self, htmltable, htmlpage, default_year):
		self.htmltable 	= htmltable
		self.htmlpage	= htmlpage
		self.items 		= htmlpage.items
		self.default_year	= default_year
		self.table_hierarchy = []
		for i in range(2):
			self.table_hierarchy.append([-2] * len(self.htmltable.idx))
		self.calculate_hierarchy(HIERARCHY_DIR_UP)
		self.calculate_hierarchy(HIERARCHY_DIR_LEFT)
		self.years = []
		self.find_all_year_rows()
		

		
	
	
	
	