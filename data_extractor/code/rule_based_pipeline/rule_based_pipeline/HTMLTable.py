# ============================================================================================================================
# PDF_Analyzer
# File   : HTMLTable.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 HTMLTable referes to * HTMLItems
# Note   : 1 HTMLPage consistens of * HTMLTables
# ============================================================================================================================

from globals import *
from HTMLItem import *
from ConsoleTable import *



class HTMLTable:
	# refers to a table extracted by the HTML-files, to which PDFs have been converted
	# this is not related with an acutal table in HTML syntax
	
	rows 		= None
	cols 		= None
	idx			= None
	num_rows	= None
	num_cols	= None
	items		= None #dont export
	marks		= None
	col_aligned_pos_x 	= None
	headline_idx		= None
	special_idx			= None # e.g., annonations
	table_rect 			= None

	
	def __init__(self):
		self.rows = []
		self.cols = []
		self.idx = []
		self.items = []
		self.num_rows = 0
		self.num_cols = 0
		self.marks = []
		self.col_aligned_pos_x  = []
		self.headline_idx = []
		self.special_idx = []
		self.table_rect = Rect(99999,99999,-1,-1)


	def get_ix(self, i, j): # i=row, j=col
		return i * self.num_cols + j
		
	def get_row_and_col_by_ix(self, ix):
		return ix//self.num_cols, ix%self.num_cols
		

	def get_idx(self, i, j): # i=row, j=col
		return self.idx[i * self.num_cols + j]
		
	def get_item(self, i, j): # i=row, j=col
		ix = self.get_idx(i, j)
		return self.items[ix] if ix >= 0 else None
		
	def get_item_by_ix(self, i): # i=ix
		if(i < 0):
			return None
		ix = self.idx[i]
		return self.items[self.idx[i]] if ix >= 0 else None
		
	def has_item_at_ix(self, i): # i=ix
		if(i < 0):
			return False
		return self.idx[i] >= 0
		
	def has_item_at(self, i, j): # i=row, j=col
		return self.idx[i * self.num_cols + j] >= 0
		
	def has_non_empty_item_at(self, i, j):
		return self.has_item_at(i, j) and self.get_item(i, j).txt != ''
		
	def count_marks(self, mark):
		return self.marks.count(mark)
		
	def reset_marks(self):
		for i in range(len(self.marks)):
			self.marks[i] = 0 if self.idx[i] >= 0 else 9999999
			
	def set_temp_assignment(self, value=1):
		for i in self.idx:
			self.items[i].temp_assignment = value
			
	def count_actual_items(self):
		return len(self.idx) - self.idx.count(-1)
		
	def get_all_idx(self):
		return self.idx + self.headline_idx + self.special_idx
		
	def find_applying_special_item_ix(self, r0):
		# precondition : special_idx must be sorted pos_y ascending
		for i in range(len(self.special_idx)-1, -1, -1):
			if(self.rows[r0].y0 + self.items[self.special_idx[i]].height * 0.2 >= self.items[self.special_idx[i]].pos_y):
				return i
		return None

	def find_applying_special_item(self, r0):
		ix = self.find_applying_special_item_ix(r0)
		return None if ix is None else self.items[self.special_idx[ix]]

		
	def find_special_item_idx_in_rect(self, rect):
		res = []
		for i in self.special_idx:
			if(Rect.calc_intersection_area(self.items[i].get_rect(), rect) / self.items[i].get_rect().get_area() > 0.1):
				res.append(i)
		return res
		
	def find_nearest_cell_ix(self, item):
		pos_x = item.get_aligned_pos_x()
		pos_y = item.pos_y + item.height
		r0 = self.num_rows-1
		c0 = self.num_cols-1
		for c in range(len(self.cols)):
			if(self.cols[c].x0 > pos_x):
				c0 = max(0, c-1)
				break
				
		for r in range(len(self.rows)):
			if(self.rows[r].y0 > pos_y):
				r0 = max(0, r-1)
				break
		
		return self.get_ix(r0, c0)

	def count_regular_items_in_rect(self, rect):
		res = 0
		for it in self.items:
			if(it.category in [CAT_HEADLINE, CAT_OTHER_TEXT, CAT_RUNNING_TEXT, CAT_FOOTER] and Rect.calc_intersection_area(it.get_rect(), rect) / it.get_rect().get_area() > 0.1  ):
				res += 1
		return res
			
	def unfold_idx_to_items(self, idx_list):
		res = []
		for i in idx_list:
			res.append(self.items[i])
		return res
		
	def unfold_ix_to_idx(self, ix_list):
		res = []
		for i in ix_list:
			res.append(self.idx[i])
		return res
		
		
	def find_applying_special_item(self, r0):
		# precondition : special_idx must be sorted pos_y ascending
		ix = self.find_applying_special_item_ix(r0)
		return self.items[self.special_idx[ix]] if ix is not None else None
		
	def find_first_non_empty_row_in_col(self, c0):
		for i in range(self.num_rows):
			if(self.has_item_at(i, c0)):
				return i
		return self.num_rows
		
		
		
	def col_looks_like_text_col(self, c0):
		num_numbers = 0
		num_words = 0
		for i in range(self.num_rows):
			if(self.has_item_at(i, c0)):
				txt = self.get_item(i, c0).txt
				#print(txt)
				if(Format_Analyzer.looks_numeric(txt)):
					num_numbers += 1
					#print('.. looks numeric')
				elif(Format_Analyzer.looks_words(txt)):
					num_words += 1
					#print('.. looks words')
		return num_words >= 5 and num_words > num_numbers * 0.3
	
	def get_all_cols_as_text(self, c0):
		res = []
		for i in range(self.num_rows):
			if(self.has_item_at(i, c0)):
				txt = self.get_item(i, c0).txt
				res.append(txt)
		return res
		
	
			
	def recalc_geometry(self):
	

		self.rows = []
		self.cols = []
		self.col_aligned_pos_x  = []	

		table_rect = Rect(9999999, 9999999, -1, -1)
		
		# Calc table rect
		for i in range(self.num_rows):
			for j in range(self.num_cols):
				if(self.has_item_at(i, j)):
					table_rect.grow(self.get_item(i, j).get_rect())
					
		self.table_rect = table_rect
				
		# Calc row rects
		for i in range(self.num_rows):
			row_rect = Rect(table_rect.x0, 9999999, table_rect.x1, table_rect.y1)
			for j in range(self.num_cols):
				if(self.has_item_at(i, j)):
					row_rect.y0 = min(row_rect.y0, self.get_item(i, j).pos_y)
			self.rows.append(row_rect)
			if(i>0):
				self.rows[i-1].y1 = max(row_rect.y0, self.rows[i-1].y0+1)
		
		# Calc column rects
		for j in range(self.num_cols):
			col_rect = Rect(9999999, table_rect.y0, table_rect.x1, table_rect.y1)
			for i in range(self.num_rows):
				if(self.has_item_at(i, j)):
					col_rect.x0 = min(col_rect.x0, self.get_item(i, j).pos_x)
			self.cols.append(col_rect)
			if(j>0):
				self.cols[j-1].x1 = max(col_rect.x0, self.cols[j-1].x0+1) 
				
		# Calc column aligned positions
		for j in range(self.num_cols):
			# find main alignment
			ctr_left = 0
			ctr_right = 0
			ctr_center = 0 # New-27.06.2022
			for i in range(self.num_rows):
				if(self.has_item_at(i,j)):
					if(self.get_item(i,j).alignment == ALIGN_LEFT):
						ctr_left += 1
					elif(self.get_item(i,j).alignment == ALIGN_RIGHT):
						ctr_right += 1
					else:
						ctr_center += 1
				
			
			#col_alignment = ALIGN_LEFT if ctr_left >= ctr_right  else ALIGN_RIGHT
			col_alignment = ALIGN_LEFT #default
			if(ctr_left >= ctr_right and ctr_left >= ctr_center):
				col_alignment = ALIGN_LEFT
			elif(ctr_right >= ctr_left and ctr_right >= ctr_center):
				col_alignment = ALIGN_RIGHT
			else:
				col_alignment = ALIGN_CENTER
				
			
			sum_align_pos_x = 0
			ctr = 0
			
			for i in range(self.num_rows):
				if(self.has_item_at(i, j)):
					# New-27.06.2022
					#sum_align_pos_x += self.get_item(i, j).pos_x if col_alignment == ALIGN_LEFT else (self.get_item(i, j).pos_x + self.get_item(i, j).width)
					to_add = 0
					if(col_alignment == ALIGN_LEFT):
						to_add = self.get_item(i, j).pos_x
					if(col_alignment == ALIGN_RIGHT):
						to_add = self.get_item(i, j).pos_x + self.get_item(i, j).width
					if(col_alignment == ALIGN_CENTER):
						to_add = self.get_item(i, j).pos_x + self.get_item(i, j).width * 0.5
					sum_align_pos_x +=  to_add
					
					ctr += 1
			
			self.col_aligned_pos_x.append(sum_align_pos_x / ctr if ctr > 0 else -1)		
				
				
	def insert_row(self, r0): # row will be inserted AFTER r0
		if(r0 < -1 or r0 > self.num_rows):
			raise ValueError('Rows r0='+str(r0)+' out of range.')		
		
		c = self.num_cols
		self.idx = self.idx[0:c*(r0+1)] + ([-1] * c) + self.idx[c*(r0+1):]
		self.marks = self.marks[0:c*(r0+1)] + ([9999999] * c) + self.marks[c*(r0+1):]
		self.num_rows += 1
		
	def is_row_insertion_possible(self, r0, pos_y): # can we insert row, starting at pos_y, right below r0?
		
		y1 = self.rows[r0].y0
		for j in range(self.num_cols):
			if(self.has_item_at(r0, j)):
				y1 = max(y1, self.get_item(r0, j).get_rect().y1)
		
		return pos_y > y1

	def delete_rows(self, r0, r1, do_recalc_geometry = True): #delete rows r, where r0 <= r < r1
		if(r0 < 0 or r0 > self.num_rows):
			raise ValueError('Rows r0='+str(r0)+' out of range.')
		if(r1 < 0 or r1 > self.num_rows):
			raise ValueError('Rows r1='+str(r1)+' out of range.')
		if(r1 <= r0):
			raise ValueError('Rows r1='+str(r1)+' <= r0='+str(r0))
		
		c = self.num_cols
		self.idx = self.idx[0:c*r0] + self.idx[c*r1:]
		self.marks = self.marks[0:c*r0] + self.marks[c*r1:]
		self.num_rows -= (r1-r0)
		if(do_recalc_geometry):
			self.recalc_geometry()
		
	def delete_cols(self, c0, c1, do_recalc_geometry = True): #delete cols c, where c0 <= c < c1
		if(c0 < 0 or c0 > self.num_cols):
			raise ValueError('Cols c0='+str(c0)+' out of range.')
		if(c1 < 0 or c1 > self.num_cols):
			raise ValueError('Cols c1='+str(c1)+' out of range.')
		if(c1 <= c0):
			raise ValueError('Cols c1='+str(c1)+' <= c0='+str(c0))
		
		c = self.num_cols
		tmp_idx = []
		tmp_marks = []
		for i in range(self.num_rows):
			tmp_idx += self.idx[i*c:i*c+c0] + self.idx[i*c+c1:(i+1)*c]
			tmp_marks += self.marks[i*c:i*c+c0] + self.marks[i*c+c1:(i+1)*c]
			
		self.idx = tmp_idx
		self.marks = tmp_marks
		self.num_cols -= (c1-c0)
		if(do_recalc_geometry):
			self.recalc_geometry()
			
	def is_row_mergable(self, r0): # return True iff row r0 and r0+1 can be merged
		if(r0 < 0 or r0 >= self.num_rows - 1):
			raise ValueError('Rows r0='+str(r0)+' and r0+1 out of range.')
			
		y0_max = 0
		y1_min = 9999999
		for j in range(self.num_cols):
			if(self.has_item_at(r0, j) and self.has_item_at(r0+1, j) and not self.get_item(r0,j).is_mergable(self.get_item(r0+1,j))):
				return False
			cur_y0 = self.get_item(r0, j).pos_y + self.get_item(r0, j).height if self.has_item_at(r0, j) else 0
			cur_y1 = self.get_item(r0+1, j).pos_y if self.has_item_at(r0+1, j) else 9999999
			y0_max = max(y0_max, cur_y0)
			y1_min = min(y1_min, cur_y1)
		

		if(y0_max < y1_min):
			return False # rows would not overlap
			
		#rows are overlapping, now check for items what would block merging
		
		c0 = 0
		c1 = 0
		r1 = r0+1
		while(c0 < self.num_cols and c1 < self.num_cols):
			if(self.has_item_at(r0, c0) and self.has_item_at(r1, c1)):
				x0_0 = self.get_item(r0, c0).pos_x
				x1_0 = self.get_item(r0, c0).pos_x+self.get_item(r0, c0).width
				x0_1 = self.get_item(r1, c1).pos_x
				x1_1 = self.get_item(r1, c1).pos_x+self.get_item(r1, c1).width
				if(min(x1_0, x1_1) - max(x0_0, x0_1) >= 0):
					print_verbose(7, "-----> Can't merge rows "+str(r0)+" and next one, because c0="+str(c0)+", c1="+str(c1)+" would overlap")
					print_verbose(7, "These are the items "+str(self.get_item(r0,c0))+", and "+str(self.get_item(r1,c1)))
					return False # two columns would overlaping in the same row
				if(x1_0 < x1_1):
					c0 += 1
				else:
					c1 += 1
			elif(self.has_item_at(r0, c0)):
				c1 += 1
			else:
				c0 += 1
				
		print_verbose(7, "----> Merge r0="+str(r0)+" where y0_max,y1_min = "+str(y0_max)+","+str(y1_min))
		return True
			
			
	def is_col_mergable(self, c0): # return True iff col c0 and c0+1 can be merged
		if(c0 < 0 or c0 >= self.num_cols -1):
			raise ValueError('Cols c0='+str(c0)+' and c0 out of range')
			
		for i in range(self.num_rows):
			if(self.has_item_at(i, c0) and self.has_item_at(i, c0+1)):
				return False
		
		return True
			
			
	def merge_rows(self, r0, reconnect=False): # merge rows r0 and r0+1
		if(r0 < 0 or r0 >= self.num_rows - 1):
			raise ValueError('Rows r0='+str(r0)+' and r0+1 out of range.')

		for j in range(self.num_cols):
			ix0 = self.get_ix(r0, j)
			ix1 = self.get_ix(r0+1, j)
			if(self.idx[ix0]==-1):
				self.idx[ix0] = self.idx[ix1]
			elif(self.idx[ix1]==-1):
				#self.idx[ix0] = ix0
				pass
			else:
				if(reconnect):
					#print("\n\n\n\nRECONNECT: "+str(self.items[self.idx[ix0]].this_id) + " <-> " + str(self.items[self.idx[ix1]].this_id))#zz
					self.items[self.idx[ix0]].reconnect(self.items[self.idx[ix1]], self.items)
				self.items[self.idx[ix0]].merge(self.items[self.idx[ix1]])
				#if(reconnect):#zz
				#	print("After reconnect: "  + str(self.items))#zz
		self.delete_rows(r0+1, r0+2, False)
		
	def merge_cols(self, c0): # merge cols c0 and c0+1
		if(c0 < 0 or c0 >= self.num_cols -1):
			raise ValueError('Cols c0='+str(c0)+' and c0 out of range')
		
		for i in range(self.num_rows):
			ix0 = self.get_ix(i, c0)
			ix1 = self.get_ix(i, c0+1)
			if(self.idx[ix0] == -1):
				self.idx[ix0] = self.idx[ix1]
		
		self.delete_cols(c0+1, c0+2, False)
			
		
		
	def merge_down_all_rows(self):
		#print_subset(0, self.items, self.idx)
		for i in range(self.num_rows-1):
			if(self.is_row_mergable(i)):
				self.merge_rows(i)
				self.merge_down_all_rows()
				return
				
	def merge_down_all_cols(self):
		for j in range(self.num_cols-1):
			if(self.is_col_mergable(j)):
				self.merge_cols(j)
				self.merge_down_all_cols()
				return
		
		
		
	def is_empty_row(self, r):
		for j in range(self.num_cols):
			if(self.has_item_at(r, j)):
				return False
		return True
		
	def is_empty_col(self, c):
		for i in range(self.num_rows):
			if(self.has_item_at(i, c)): # and self.get_item(i,c).txt != ''):
				#print('HAS ITEM AT '+str(i)+','+str(c)+', namely: '+str(self.get_item(i,c)))
				return False
		return True
		
	def compactify(self): #remove all empty rows and cols
		
		has_changed = True
		while(has_changed):
			has_changed = False
			#rows
			for i in range(self.num_rows-1, -1, -1):
				if(self.is_empty_row(i)):
					print_verbose(7, "Delete empty row : "+str(i))
					has_changed = True
					self.delete_rows(i, i+1, False)
			#cols
			for j in range(self.num_cols-1, -1, -1):
				if(self.is_empty_col(j)):
					print_verbose(7, "Delete empty column : "+str(j))
					has_changed = True
					self.delete_cols(j, j+1, False)
					
		self.recalc_geometry()
			


	def throw_away_non_connected_rows(self): # throw away rows that are probably not connected to the table
		def is_connected_row(r0):
			min_y0 = 9999999
			max_y0 = -1
			min_y1 = 9999999
			for j in range(self.num_cols):
				if(self.has_item_at(r0, j)):
					min_y0 = min(min_y0, self.get_item(r0, j).pos_y)
					max_y0 = max(max_y0, self.get_item(r0, j).pos_y + self.get_item(r0, j).height)
				if(self.has_item_at(r0+1, j)):
					min_y1 = min(min_y1, self.get_item(r0+1, j).pos_y)
			
			if(min_y1 == 9999999 or min_y0 == 9999999):
				return True# at least one row was empty => consider always as connected
			
			
			y_limit = min_y0 + (max_y0 - min_y0) * config.global_row_connection_threshold  #at least space that woulld occupy 4x row r0 are (not) empty #New: 27.06.2022 (was previously: * 4)
			
			if(min_y1 <= y_limit):
				return True
			
			sp_idx = self.find_special_item_idx_in_rect(self.rows[r0])
			
			for k in sp_idx:
				cur_y = self.items[k].pos_y
				if(cur_y <= y_limit):
					return True
			
			return False
				

		for i in range(self.num_rows-1):
			if(not is_connected_row(i)):
				print_verbose(5, "Throw away non-connected rows after /excl. :"+str(i))
				print_verbose(5, "Current table: "+str(self))
				self.delete_rows(i+1, self.num_rows)
				return

	def throw_away_rows_after_new_header(self):
			
		if(self.num_cols < 2 or self.num_rows < 3):
			return
			
		num_numeric_rows = 0
		num_rows_with_left_txt = 0
		last_pos_y = 9999999
		last_delta_y = 9999999
		
		for i in range(self.num_rows):
			if(self.has_item_at(i,0) and Format_Analyzer.looks_words(self.get_item(i,0).txt)):
				num_rows_with_left_txt += 1
			cur_numeric_values = 0
			cur_header_values = 0
			cur_other_values = 0
			cur_pos_y = 9999999
			for j in range(1, self.num_cols):
				if(self.has_item_at(i,j)):
					if(cur_pos_y == 9999999):
						cur_pos_y = self.get_item(i,j).pos_y
					txt = self.get_item(i,j).txt
					if(Format_Analyzer.looks_numeric(txt) and not Format_Analyzer.looks_year(txt)):
						cur_numeric_values += 1
					elif((Format_Analyzer.looks_words(txt) and txt[0].isupper()) or Format_Analyzer.looks_year(txt)):
						cur_header_values += 1
					else:
						cur_other_values += 1
					
			if(cur_numeric_values > max(self.num_cols * 0.6,1)):
				num_numeric_rows += 1
			
			cur_delta_y = cur_pos_y - last_pos_y
				
			if(num_rows_with_left_txt > 2 and num_numeric_rows > 2 and cur_delta_y > last_delta_y * 1.05 + 2):
				if(cur_numeric_values == 0 and cur_header_values > 0 and cur_other_values == 0):	
					print_verbose(5, "Throw away non-connected rows after probably new headline at row = "+str(i)+", cur/last_delta_y="+str(cur_delta_y)+"/"+str(last_delta_y))
					self.delete_rows(i, self.num_rows)
					return
			
			last_pos_y = cur_pos_y
			last_delta_y = cur_delta_y
				
			
	def throw_away_last_headline(self):
		# a headline at the end of a table probably doesnt belong to it, rather, it belongs to the next table
		if(self.num_rows < 2 or self.num_cols < 2):
			return
			
		if(not self.has_non_empty_item_at(self.num_rows-1, 0)):
			return
			
		if(Format_Analyzer.looks_numeric(self.get_item(self.num_rows-1, 0).txt)):
			return
			
		for j in range(1, self.num_cols):
			if(self.has_non_empty_item_at(self.num_rows-1, j)):
				return
		
		self.delete_rows(self.num_rows-1, self.num_rows)
			
	
				
				
	def throw_away_non_connected_cols(self, page_width): # throw away cols that are probably not connected to the table
		def is_connected_col(c0):
			min_x0 = 9999999
			max_x0 = -1
			min_x1 = 9999999
			for i in range(self.num_rows):
				if(self.has_item_at(i, c0)):
					min_x0 = min(min_x0, self.get_item(i, c0).pos_x)
					max_x0 = max(max_x0, self.get_item(i, c0).pos_x + self.get_item(i, c0).width)
				if(self.has_item_at(i, c0+1)):
					min_x1 = min(min_x1, self.get_item(i, c0+1).pos_x)
			
			if(min_x1 == 9999999 or min_x0 == 9999999):
				return True# at least one col was empty => consider always as connected
			
			if (min_x1 <= max_x0  + DEFAULT_HTHROWAWAY_DIST * page_width): #at least that much space is not empty
				return True
				
		
			num_reg_text = 0
			for i in range(self.num_rows):
				if(not self.has_item_at(i,c0)):
					continue
				y0 = self.get_item(i, c0).pos_y
				y1 = self.get_item(i, c0).pos_y + self.get_item(i, c0).height
				x0 = max((min_x0 + max_x0)/2.0, self.get_item(i, c0).pos_x)
				x1 = min_x1
				cur_rect = Rect(x0, y0, x1, y1)
				for it in self.items:
					if(it.category not in [CAT_HEADLINE, CAT_OTHER_TEXT, CAT_RUNNING_TEXT, CAT_FOOTER]):
						continue
					it_rect = it.get_rect()
					if(Rect.calc_intersection_area(cur_rect, it_rect) > 0):
						print_verbose(2, '----->> With ' +str(self.get_item(i, c0))+ ' the item ' +str(it) + ' overlaps')		
						num_reg_text += 1
			
			
			#num_reg_text = self.count_regular_items_in_rect(Rect( (min_x0 + max_x0)/2.0, self.table_rect.y0, min_x1, self.table_rect.y1) )
			
			return num_reg_text == 0
				
		
		for j in range(self.num_cols-1):
			if(not is_connected_col(j)):
				print_verbose(5, "Throw away non-connected cols after /excl. :"+str(j))
				print_verbose(5, "Current table: "+str(self))
				self.delete_cols(j+1, self.num_cols)
				return
				
				
	def throw_away_cols_at_next_paragraph(self, paragraphs):
		def find_cur_paragraph_idx(x0, x1, my_paragraphs):
			max_overlap = 0
			res = -1
			for i in range(len(my_paragraphs)):
				p0 = my_paragraphs[i]
				p1 = my_paragraphs[i+1] if i < len(my_paragraphs) -1 else 9999999
				overlap = max(min(x1, p1) - max(x0, p0), 0)
				if(overlap > max_overlap):
					max_overlap = overlap
					res = i
			return res
				
				
		
		if(self.num_cols == 0 or len(paragraphs) < 2):
			return
			
		self.recalc_geometry()
			
		# Find relevant paragraphs
		my_paragraphs = []
		for p in paragraphs:
			cnt = 0
			for it in self.items:
				if(it.pos_x == p and it.category in (CAT_RUNNING_TEXT , CAT_HEADLINE) and it.pos_x < self.table_rect.x1 and it.pos_x+it.width > self.table_rect.x0):
					if((it.pos_y < self.table_rect.y1 and it.pos_y + it.height * 5 > self.table_rect.y0) or #TODO 5 was 10, test it
					   (it.pos_y > self.table_rect.y0 and it.pos_y - it.height * 5 < self.table_rect.y1)): #TODO 5 was 10, test it
						cnt += 1
						#print(it)
			if(cnt > 3):
				my_paragraphs.append(p)
		
		my_paragraphs.sort()
		
		print_verbose(5, "Relevant paragraphs:"+str(my_paragraphs))
		
		
		last_para_idx = -1
		
		for j in range(self.num_cols):
			x0 = 9999999
			x1 =  -1
			for i in range(self.num_rows):
				if(self.has_item_at(i,j)):
					x0 = min(x0, self.get_item(i,j).pos_x)
					x1 = max(x1, self.get_item(i,j).pos_x + self.get_item(i,j).width)
			if(x1 == -1):
				continue #b/c empty col
					
			#print(j, x0, x1, my_paragraphs)
			cur_para_idx = find_cur_paragraph_idx(x0, x1, my_paragraphs)
			print_verbose(7, "--> Col ="+str(j) + ", x0/x1="+str(self.cols[j].x0)+"/"+str(self.cols[j].x1)+" belong to paragraph p_idx = " + str(cur_para_idx) +  ", which is at " + str(my_paragraphs[cur_para_idx] if cur_para_idx != -1 else None) + " px")
			if(j>1 and cur_para_idx != last_para_idx): #TODO 1 was 0, test is
				# table is here probably split between two text paragraphs
				print_verbose(5, "Throw away cols at next paragraph: col at next j="+str(j))
				self.delete_cols(j, self.num_cols)
				return
			last_para_idx = cur_para_idx
			
		
	
	def throw_away_cols_after_year_list(self): #throw away cols after a list of years is over
	
		class YearCols:
			r = None
			c0 = None
			c1 = None
			def __init__(self, r, c0):
				self.r=r
				self.c0=c0
			
			def __repr__(self):
				return "(r="+str(self.r)+",c0="+str(self.c0)+",c1="+str(self.c1)+")"
				
		if(self.num_cols < 5):
			return 
	
		year_cols = [] 
		
		#print(str(self))
		#print("Cols:"+str(self.num_cols))
		
		for i in range(self.num_rows):
			j = 0
			while(j < self.num_cols - 1):
				if(self.has_item_at(i,j) and self.has_item_at(i,j+1) and \
				   Format_Analyzer.looks_year(self.get_item(i,j).txt) and \
				   Format_Analyzer.looks_year(self.get_item(i,j+1).txt) and \
				   abs(Format_Analyzer.to_year(self.get_item(i,j+1).txt) - Format_Analyzer.to_year(self.get_item(i,j).txt)) == 1):
					dir = Format_Analyzer.to_year(self.get_item(i,j+1).txt) - Format_Analyzer.to_year(self.get_item(i,j).txt)
					cur_year_cols = YearCols(i, j)
					#find last year col
					#print("Now at cell:"+str(i)+","+str(j))
					for j1 in range(j+1, self.num_cols):
						if(self.has_item_at(i,j1) and \
						   Format_Analyzer.looks_year(self.get_item(i,j1).txt) and \
						   Format_Analyzer.to_year(self.get_item(i,j1).txt) - Format_Analyzer.to_year(self.get_item(i,j1-1).txt) == dir):
							cur_year_cols.c1 = j1
						else:
							break
					year_cols.append(cur_year_cols)
					j = cur_year_cols.c1
				j += 1
				
		print_verbose(6, '----->> Found year lists at: ' +str(year_cols))
		
		
		if(len(year_cols) < 2):
			return
			
		# test if we can throw away
		
		# find min
		
		min_yc = -1
		for k in range(len(year_cols)):
			if(min_yc == -1 or (year_cols[k].c0 < year_cols[min_yc].c0)):
				min_yc = k
				
		print_verbose(6, "------->> min:" + str(year_cols[min_yc]) + " at idx " + str(min_yc))
		
		#find overlapping max
		max_overlap_yc = -1
		for k in range(len(year_cols)):
			if(year_cols[k].c0 < year_cols[min_yc].c1):
				if(max_overlap_yc == -1 or (year_cols[k].c1 > year_cols[max_overlap_yc].c1)):
					max_overlap_yc = k
		
		print_verbose(6, "------->> max overlap:" + str(year_cols[max_overlap_yc]) + " at idx " + str(max_overlap_yc))
		
		# are there any year cols after max overlap? if so, we can throw that part away
		can_throw_away = False
		for yc in year_cols:
			if(yc.c0 > year_cols[max_overlap_yc].c1):
				print_verbose(6, "-------->> throw away because : " + str(yc) )
				can_throw_away = True
				
		if(can_throw_away):
			self.delete_cols(year_cols[max_overlap_yc].c1 + 1, self.num_cols)
	
	
	def throw_away_duplicate_looking_cols(self): #throw away columns that are looking like duplicates, and indicating another table
		def are_cols_similar(c0, c1):
			return self.col_looks_like_text_col(c0) and self.col_looks_like_text_col(c1) \
			       and Format_Analyzer.cnt_overlapping_items(self.get_all_cols_as_text(c0), self.get_all_cols_as_text(c1)) > 3
	
	
		if(self.num_cols < 3):
			return
		
		for i in range(2, self.num_cols):
			if(are_cols_similar(0, i)):
				print_verbose(7, "------->> cols 0 and " + str(i) + " are similar. Throw away from " + str(i))
				self.delete_cols(i, self.num_cols)
				return
	
	
	
				
	def identify_headline(self):
		if(self.num_rows == 0 or self.num_cols == 0):
			return
		
		if(not self.has_item_at(0,0) or not Format_Analyzer.looks_words(self.get_item(0,0).txt)):
			return
			
		for j in range(1, self.num_cols):
			if(self.has_item_at(0, j)):
				return
				
		self.headline_idx.append(self.get_idx(0,0))
		self.delete_rows(0, 1)
				
				
	def identify_non_numeric_special_items(self):
		def col_looks_numeric(c0):
			num_numbers = 0
			num_words = 0
			for i in range(self.num_rows):
				if(self.has_item_at(i, c0)):
					txt = self.get_item(i, c0).txt
					if(Format_Analyzer.looks_numeric(txt)):
						num_numbers += 1
					elif(Format_Analyzer.looks_words(txt)):
						num_words += 1
			return num_numbers >= 3 and num_words < num_numbers * 0.4
		
		def is_only_item_in_row(r0, c0):
			for j in range(c0):
				if(self.has_item_at(r0, j)):
					return False
			for j in range(c0+1, self.num_cols):
				if(self.has_item_at(r0, j)):
					return False
			return True
			
		for j in range(self.num_cols):
			if(col_looks_numeric(j)):
				print_verbose(5, 'Numeric col found : '+str(j))
				# find first possible special item of this col
				r0 = self.find_first_non_empty_row_in_col(j)
				r1 = r0
				font_char = self.get_item(r0, j).get_font_characteristics()
				for i in range(r0, self.num_rows):
					r1 = i
					if(not self.has_item_at(i,j)):
						r1 = i + 1
						break #empty line
					if(Format_Analyzer.looks_numeric(self.get_item(i,j).txt)):
						r1 = i + 1
						break #number
					if(self.get_item(i,j).get_font_characteristics() != font_char):
						break #different font 

				# remove now special items (but not before first occurence)
				for i in range(r1, self.num_rows):
					if(self.has_item_at(i, j)):
						txt = self.get_item(i, j).txt	
						if(Format_Analyzer.looks_words(txt) or Format_Analyzer.looks_other_special_item(txt)):
							cur_idx = self.get_idx(i,j)
							self.idx[self.get_ix(i,j)] = -1
							self.special_idx.append(cur_idx)
							
				#remove even special items from headline, but only if there are no other headline items
				if(self.has_item_at(r0, j) and is_only_item_in_row(r0, j) and (Format_Analyzer.looks_words(self.get_item(r0, j).txt) or Format_Analyzer.looks_other_special_item(self.get_item(r0, j).txt))):
					cur_idx = self.get_idx(r0, j)
					self.idx[self.get_ix(r0,j)] = -1
					self.special_idx.append(cur_idx)
				"""
				if(self.has_item_at(0, j) and is_only_item_in_row(0, j) and (Format_Analyzer.looks_words(self.get_item(0, j).txt) or Format_Analyzer.looks_other_special_item(self.get_item(0, j).txt))):
					cur_idx = self.get_idx(0, j)
					self.idx[self.get_ix(0,j)] = -1
					self.special_idx.append(cur_idx)
				"""



	def identify_overlapping_special_items(self):
		# *  Identify all remaing items that must be set to be special items
		#    because otherwise they would overlap with other columns.
		# *  This is tricky, because we need to find a minimal set of such items,
		#    which leads to an NP-complete problem.
		# *  To solve it (fast in most cases), we employ a Backtracking algorithm

		rec_counter = 0		
		timeout = False
		t_start = 0
		looks_numeric = []
		tmp_boundaries = []
		
		def calc_single_col_boundary(tmp_idx, col0):
			cur_bdry = (9999999, -1)
			for i in range(self.num_rows):
				cur_ix = self.get_ix(i,col0)
				cur_idx = tmp_idx[cur_ix] 
				if(cur_idx != -1):
					cur_bdry =( min(cur_bdry[0], self.items[cur_idx].pos_x),  max(cur_bdry[1], self.items[cur_idx].pos_x + self.items[cur_idx].width) )
			return cur_bdry		
		
		def calc_col_boundaries(tmp_idx):
			res = [(0,0)] * self.num_cols
			
			for j in range(self.num_cols):
				res[j] = calc_single_col_boundary(tmp_idx, j)
			return res
		
		def find_first_overlapping_col(boundaries):
			for j in range(self.num_cols-1):
				if(boundaries[j][1] == -1):
					continue # skip empty columns
				
				#find nextnon-empty col
				k = j+1
				while(k<self.num_cols and boundaries[k][1] == -1):
					k+=1
					
				if(k == self.num_cols):
					return -1 # only empty columns left
				
				if(boundaries[j][0] + (boundaries[j][1] - boundaries[j][0]) * 0.99 > boundaries[k][0]):
					#0.99 tolerance, because sometimes font width is overestimated
					return j
			return -1
						
		def find_possible_overlapping_ix(c0, tmp_idx, boundaries):
			bdry = (min(boundaries[c0][0],boundaries[c0+1][0]), max(boundaries[c0][1], boundaries[c0+1][1]))
			res = []
			found_something = False
			for j in range(self.num_cols):
				if(boundaries[j][1] > bdry[0] and boundaries[j][0] < bdry[1]):
					#all items from this col might be overlaping
					for i in range(self.num_rows):
						cur_ix = self.get_ix(i,j)
						if(tmp_idx[cur_ix] != -1):
							res.append(cur_ix)
							found_something = True
			res = sorted(res, key=lambda ix: - self.items[tmp_idx[ix]].width) #sort descending
			if(not found_something):
				raise ValueError('Some columns are overlapping, but there are no relevant items.')
			return res
							

						
		def find_allowed_set_rec(tmp_idx, num_sp_items, last_sp_ix, lowest_num_so_far):
			# returns set of ix'es, such that after removing them, the rest is allowed (e.g., no overlap)
			nonlocal rec_counter
			nonlocal t_start
			nonlocal timeout
			nonlocal looks_numeric
			nonlocal tmp_boundaries
			
			rec_counter += 1
			
			if(rec_counter % 1000 == 0):
				t_now = time.time()
				if(t_now - t_start > config.global_max_identify_complex_items_timeout): #max 5 sec TODO
					timeout = True
				
			
			if(num_sp_items >= lowest_num_so_far or timeout):
				print_verbose(20,"No better solution exists")
				return 9999999, [] # we cant find a better solution
			
			first_overlapping_col = find_first_overlapping_col(tmp_boundaries)
			if(first_overlapping_col == -1):
				print_verbose(9,"Found solution, num_sp_items="+str(num_sp_items))
				return num_sp_items, [last_sp_ix] #we found allowed set, where only num_sp_items items are excluded
			

			#raise ValueError('first_overlapping_col='+str(first_overlapping_col))
			
			possible_overlap_ix = find_possible_overlapping_ix(first_overlapping_col, tmp_idx, tmp_boundaries)
			best_sp_ix = []
			
			#raise ValueError('possible_overlap_ix='+str(possible_overlap_ix))
			
			#print_verbose(15, "num_sp_item="+str(num_sp_items)+", Boundaries = "+str(tmp_boundaries)+", first_overlapping_col = " \
			#              +str(first_overlapping_col) + " lowest_num_so_far="+str(lowest_num_so_far)) # ", possible_overlap_ix= " +str(possible_overlap_ix) +

			for ix in possible_overlap_ix:
				# try this ix
				if(looks_numeric[ix]):
					continue # never use numbers as special items
				
				#if(num_sp_items==0):
				#	print_verbose(0, "---> Trying: " +str(self.items[tmp_idx[ix]]))
				
				col = ix % self.num_cols
				
				old = tmp_idx[ix]
				tmp_idx[ix] = -1
				old_bdry = tmp_boundaries[col]
				tmp_boundaries[col] = calc_single_col_boundary(tmp_idx, col)
				cur_lowest_num, cur_sp_ix = find_allowed_set_rec(tmp_idx, num_sp_items+1, ix, lowest_num_so_far)
				tmp_idx[ix] = old
				tmp_boundaries[col] = old_bdry
				if(cur_lowest_num < lowest_num_so_far):
					lowest_num_so_far = cur_lowest_num
					best_sp_ix = cur_sp_ix
				if(cur_lowest_num == num_sp_items+1):
					break # we cannot find a better solution, so escape early
			
			return lowest_num_so_far, best_sp_ix + [last_sp_ix]
				
				
		if(self.num_cols == 0):
			return # nothing to do
			
			
		tmp_idx = self.idx.copy()
		
		for cur_idx in tmp_idx:
			looks_numeric.append(Format_Analyzer.looks_numeric(self.items[cur_idx].txt))
			

		tmp_boundaries = calc_col_boundaries(tmp_idx)
		
		t_start = time.time()
		lowest_num_so_far, sp_ix = find_allowed_set_rec(tmp_idx, 0, -1, 9999999)
		t_end = time.time()
		print_verbose(3, "---> find_allowed_set_rec completed after time="+str(t_end-t_start)+"sec,  recursions="+str(rec_counter))
		
		if(timeout and lowest_num_so_far == 9999999):
			#we coulnt find a solution => give up on this table
			print_verbose(3, "---> No solution. Give up")
			#for k in range(len(self.idx)):
			#	self.special_idx.append(self.idx[k])
			#	self.idx[k] = -1
			return
		
		
		if(lowest_num_so_far == 9999999):
			#print(str(self))
			#raise ValueError('Some columns are overlapping, but after backtracking, no items were found that could be removed.')
			return
			
		# make sure, that we dont throw out too much items
		for ix in sp_ix:
			if(ix != -1):
				tmp_idx[ix] = -1	
		
		
		
		tmp_bdry = calc_col_boundaries(tmp_idx)
		#print(tmp_bdry)
		
		sp_ix_final = []
		for ix in sp_ix:
			if(ix != -1):
				#could this one stay?
				tmp_idx[ix] = self.idx[ix]
				tmp_bdry = calc_col_boundaries(tmp_idx)
				#print(self.items[self.idx[ix]].txt)
				#print(tmp_bdry)
				if(find_first_overlapping_col(tmp_bdry) != -1):
					#no, it can't
					sp_ix_final.append(ix)
					#print('----> No!')
				tmp_idx[ix] = -1
					
				
				
					
		
		
		

		for ix in sp_ix_final:
			if(ix != -1):
				self.special_idx.append(self.idx[ix])
				self.idx[ix] = -1
			
			
		self.recalc_geometry()
		
		
	
		return
			
		
		
	"""
	
	
	
	# old, slow code:

	def identify_overlapping_special_items(self):
		# *  Identify all remaing items that must be set to be special items
		#    because otherwise they would overlap with other columns.
		# *  This is tricky, because we need to find a minimal set of such items,
		#    which leads to an NP-complete problem.
		# *  To solve it (fast in most cases), we employ a Backtracking algorithm
		# TODO: Tuning!! (calc boundries only once, and then recalc only affected col; precalc looks numeric)

		rec_counter = 0		
		timeout = False
		t_start = 0
		
		def calc_col_boundaries(tmp_idx):
			res = [(0,0)] * self.num_cols
			
			for j in range(self.num_cols):
				cur_bdry = (9999999, -1)
				for i in range(self.num_rows):
					cur_ix = self.get_ix(i,j)
					cur_idx = tmp_idx[cur_ix] 
					if(cur_idx != -1):
						cur_bdry =( min(cur_bdry[0], self.items[cur_idx].pos_x),  max(cur_bdry[1], self.items[cur_idx].pos_x + self.items[cur_idx].width) )
				res[j] = cur_bdry
			return res
		
		def find_first_overlapping_col(boundaries):
			for j in range(self.num_cols-1):
				if(boundaries[j][1] == -1):
					continue # skip empty columns
				
				#find nextnon-empty col
				k = j+1
				while(k<self.num_cols and boundaries[k][1] == -1):
					k+=1
					
				if(k == self.num_cols):
					return -1 # only empty columns left
				
				if(boundaries[j][0] + (boundaries[j][1] - boundaries[j][0]) * 0.85 > boundaries[k][0]):
					#0.85x tolerance, because sometimes font width is overestimated
					return j
			return -1
						
		def find_possible_overlapping_ix(c0, tmp_idx, boundaries):
			bdry = (min(boundaries[c0][0],boundaries[c0+1][0]), max(boundaries[c0][1], boundaries[c0+1][1]))
			res = []
			found_something = False
			for j in range(self.num_cols):
				if(boundaries[j][1] > bdry[0] and boundaries[j][0] < bdry[1]):
					#all items from this col might be overlaping
					for i in range(self.num_rows):
						cur_ix = self.get_ix(i,j)
						if(tmp_idx[cur_ix] != -1):
							res.append(cur_ix)
							found_something = True
			res = sorted(res, key=lambda ix: - self.items[tmp_idx[ix]].width) #sort descending
			if(not found_something):
				raise ValueError('Some columns are overlapping, but there are no relevant items.')
			return res
							

						
		def find_allowed_set_rec(tmp_idx, num_sp_items, sp_ix, lowest_num_so_far):
			# returns set of ix'es, such that after removing them, the rest is allowed (e.g., no overlap)
			nonlocal rec_counter
			nonlocal t_start
			nonlocal timeout
			rec_counter += 1
			
			if(rec_counter % 1000 == 0):
				t_now = time.time()
				if(t_now - t_start > 5.0): #max 5 sec TODO
					timeout = True
				
			
			if(num_sp_items >= lowest_num_so_far or timeout):
				print_verbose(20,"No better solution exists")
				return 9999999, [] # we cant find a better solution
			
			boundaries = calc_col_boundaries(tmp_idx)
			first_overlapping_col = find_first_overlapping_col(boundaries)
			if(first_overlapping_col == -1):
				print_verbose(9,"Found solution, num_sp_items="+str(num_sp_items))
				return num_sp_items, sp_ix #we found allowed set, where only num_sp_items items are excluded
			
				
			possible_overlap_ix = find_possible_overlapping_ix(first_overlapping_col, tmp_idx, boundaries)
			best_sp_ix = None
			
			
			print_verbose(15, "num_sp_item="+str(num_sp_items)+", Boundaries = "+str(boundaries)+", first_overlapping_col = " \
			              +str(first_overlapping_col) + " lowest_num_so_far="+str(lowest_num_so_far)) # ", possible_overlap_ix= " +str(possible_overlap_ix) +

			for ix in possible_overlap_ix:
				# try this ix
				if(Format_Analyzer.looks_numeric(self.items[tmp_idx[ix]].txt)):
					continue # never use numbers as special items
				print_verbose(20, "---> Trying: " +str(self.items[tmp_idx[ix]]))
				old = tmp_idx[ix]
				tmp_idx[ix] = -1
				cur_lowest_num, cur_sp_ix = find_allowed_set_rec(tmp_idx, num_sp_items+1, sp_ix + [ix], lowest_num_so_far)
				tmp_idx[ix] = old
				if(cur_lowest_num < lowest_num_so_far):
					lowest_num_so_far = cur_lowest_num
					best_sp_ix = cur_sp_ix
				if(cur_lowest_num == num_sp_items+1):
					break # we cannot find a better solution, so escape early
			
			return lowest_num_so_far, best_sp_ix
				
				
		if(self.num_cols == 0):
			return # nothing to do
			
			
		tmp_idx = self.idx.copy()
		
		#boundaries = calc_col_boundaries(tmp_idx)
		#print(self)
		#print(boundaries)
		#raise ValueError('xxxx')
		
		t_start = time.time()
		lowest_num_so_far, sp_ix = find_allowed_set_rec(tmp_idx, 0, [], 9999999)
		t_end = time.time()
		print_verbose(3, "---> find_allowed_set_rec completed after time="+str(t_end-t_start)+"sec,  recursions="+str(rec_counter))
		
		if(timeout and lowest_num_so_far == 9999999):
			#we coulnt find a solution => give up on this table
			print_verbose(3, "---> No solution. Give up")
			#for k in range(len(self.idx)):
			#	self.special_idx.append(self.idx[k])
			#	self.idx[k] = -1
			return
		
		
		if(lowest_num_so_far == 9999999):
			#print(str(self))
			#raise ValueError('Some columns are overlapping, but after backtracking, no items were found that could be removed.')
			return
		
		for ix in sp_ix:
			self.special_idx.append(self.idx[ix])
			self.idx[ix] = -1
			
			
		self.recalc_geometry()
		
		
	
		return
				
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	"""


				
	"""def identify_remaining_special_items(self, page_width):
		# return True iff something was found and changed
		for i in range(self.num_rows):
			for j in range(self.num_cols):
				if(self.has_item_at(i,j) and self.get_item(i,j).width > self.cols[j].get_width() + DEFAULT_SPECIAL_ITEM_CUTOFF_DIST * page_width \
				    and not Format_Analyzer.looks_numeric(self.get_item(i,j).txt)):
					print_verbose(5, "--> identify_remaining_special_items : "+str(self.get_item(i,j)))
					cur_idx = self.get_idx(i, j)
					self.idx[self.get_ix(i,j)] = -1
					self.special_idx.append(cur_idx)			
					return True
		return False
	"""			
					
				
				
				
					
					
	def throw_away_distant_special_items(self, page_width):
		tmp = []
		for i in self.special_idx:
			dist = Rect.distance(self.table_rect, self.items[i].get_rect()) / page_width
			if(dist <= DEFAULT_SPECIAL_ITEM_MAX_DIST and self.items[i].pos_y <= self.table_rect.y1):
				tmp.append(i)
			else:
				print_verbose(5, "Throw away special item: "+str(self.items[i]) + " from table with rect : " + 
			                     str(self.table_rect) + " and distance: " + str(dist))
		self.special_idx = sorted(tmp, key=lambda i: self.items[i].pos_y )
				
		
	
			
	def cleanup_table(self, page_width, paragraphs):
	
		bak_items = deepcopy(self.items)
		bak_idx = deepcopy(self.idx)

		num_cells = -1
		old_num_actual_items = -1
		old_num_rows = -1
		old_num_cols = -1
		
		#global config.global_verbosity
		#config.global_verbosity = 6
		
		
		print_verbose(3, 'Table before cleanup: '+str(self))
		
		
		
		
		while(True):
			cur_num_actual_items = self.count_actual_items()
			if(cur_num_actual_items == old_num_actual_items and self.num_rows == old_num_rows and self.num_cols == old_num_cols):
				break #no more changes
			
			old_num_actual_items = cur_num_actual_items
			old_num_rows = self.num_rows
			old_num_cols = self.num_cols
			
			
			print_verbose(3, "--> Next cleanuptable iteration")
			self.compactify()
			print_verbose(6, "------>> After compactify:" + str(self.get_printed_repr()))

			self.recalc_geometry()
			print_verbose(6, "------>> After recalc_geometry:" + str(self.get_printed_repr()))

			self.compactify()
			self.throw_away_non_connected_rows()
			print_verbose(6, "------>> After throw_away_non_connected_rows:" + str(self.get_printed_repr()))

			self.compactify()
			self.throw_away_rows_after_new_header()
			print_verbose(6, "------>> After throw_away_rows_after_new_header:" + str(self.get_printed_repr()))

			self.compactify()
			self.throw_away_non_connected_cols(page_width) 
			print_verbose(6, "------>> After throw_away_non_connected_cols:" + str(self.get_printed_repr()))

			self.compactify()
			self.throw_away_cols_at_next_paragraph(paragraphs)
			print_verbose(6, "------>> After throw_away_cols_at_next_paragraph:" + str(self.get_printed_repr()))
			
			self.compactify()
			self.throw_away_cols_after_year_list()
			print_verbose(6, "------>> After throw_away_cols_after_year_list:" + str(self.get_printed_repr()))

			self.compactify()
			self.throw_away_duplicate_looking_cols()
			print_verbose(6, "------>> After throw_away_duplicate_looking_cols:" + str(self.get_printed_repr()))
			
			self.compactify()
			self.merge_down_all_rows()
			print_verbose(6, "------>> After merge_down_all_rows:" + str(self.get_printed_repr()))

			self.compactify()
			self.merge_down_all_cols()
			print_verbose(6, "------>> After merge_down_all_cols:" + str(self.get_printed_repr()))

			self.compactify()
			self.identify_headline()
			print_verbose(6, "------>> After identify_headline:" + str(self.get_printed_repr()))
			
			self.compactify()
			self.throw_away_last_headline()
			print_verbose(6, "------>> After throw_away_last_headline:" + str(self.get_printed_repr()))

			self.compactify()
			self.identify_overlapping_special_items()
			print_verbose(6, "------>> After identify_overlapping_special_items:" + str(self.get_printed_repr()))
			#raise ValueError('XXX')

			self.compactify()
			self.identify_non_numeric_special_items()
			print_verbose(6, "------>> After identify_non_numeric_special_items:" + str(self.get_printed_repr()))
			
			self.compactify()
			self.recalc_geometry()
			print_verbose(6, "------>> After recalc_geometry:" + str(self.get_printed_repr()))
				

		self.compactify()

		self.special_idx = sorted(self.special_idx, key=lambda i: self.items[i].pos_y )
		self.throw_away_distant_special_items(page_width)
		
		print_verbose(6, "------>> After throw_away_distant_special_items:" + str(self.get_printed_repr()))
		
		# restore all items that are no longer part of that table
		to_restore = list(set(bak_idx) - set(self.idx + [-1]))
		print_verbose(3, "Restoring old items with idx: "+str(to_restore))
		for i in to_restore:
			# was this item merged and the merged item is still used?
			was_merged = False
			for k in self.items[i].merged_list:
				if k in self.idx:
					was_merged = True
					break
			if(not was_merged):
				print_verbose(6, '----> Old item '+str(i)+' was not merged => Restore')
				self.items[i] = bak_items[i]
			else:
				print_verbose(6, '----> Old item '+str(i)+' was merged => Dont touch')
				
				
				
				
				
		self.compactify()		
				
		print_verbose(6, "------>> After restoring old item:" + str(self.get_printed_repr()))
		
		print_verbose(3, "===============>>>>>>>>>>>>>>>> Cleanup done <<<<<<<<<<<< =====================")
		

		
				
			
	"""
	TODO :doest really work, remove in the future
	def unfold_patched_numbers(self):
		def doit(strict_alignment):
		
			#sometimes, numbers are stored in single HTMLItem, e.g. "123 456". But this should be unfolded to two cells "123", "456"
			for j in range(self.num_cols):
				for i in range(self.num_rows):
					if(not self.has_item_at(i,j)):
						continue
						
					print_verbose(7, '---> Analyze: "'+ self.get_item(i,j).txt + '", align=' +('L' if self.get_item(i,j).alignment == ALIGN_LEFT else 'R'))
					
					
					nj = -1
					if(strict_alignment):
						nj = j+1 if self.get_item(i,j).alignment == ALIGN_LEFT else j-1
					else:
						nj = j+1 if j < self.num_cols -1 and not self.has_item_at(i,j+1) else j-1

					if(nj < 0 or nj >= self.num_cols):
						continue # impossible
						
					if(not self.has_item_at(i,nj)):
						print_verbose(7, '------> next col='+str(nj)+' is empty')
						txt = Format_Analyzer.trim_whitespaces(self.get_item(i,j).txt)

						if(not Format_Analyzer.looks_numeric_multiple(txt)):
							print_verbose(7, '------> but txt="'+str(txt)+'" is not numeric.')
							continue

						if(txt.count(' ')==0):
							print_verbose(7, '------> but txt="'+str(txt)+' has no spaces.')
							continue
						
						print_verbose(7, '-------> can be split up')
						cur = ''
						rest = txt
						while(cur == '' or not Format_Analyzer.looks_numeric(cur)):
							p = rest.find(' ')
							cur += rest[:p]
							rest = rest[p+1:]
						if(rest != ''):
							print_verbose(5,'---------> Split "'+txt+'" into cur="'+cur+'", rest="'+rest+'"')
							ix1 = self.get_ix(i,j)
							ix2 = self.get_ix(i,nj)
							
							new_item = HTMLItem()
							new_item.line_num 		= self.items[self.idx[ix1]].line_num 		
							new_item.tot_line_num	= self.items[self.idx[ix1]].tot_line_num	
							new_item.pos_x 			= self.col_aligned_pos_x[nj] 
							new_item.pos_y 			= self.items[self.idx[ix1]].pos_y 			
							#new_item.width			= self.items[self.idx[ix1]].width			
							new_item.height			= self.items[self.idx[ix1]].height			
							new_item.font_size		= self.items[self.idx[ix1]].font_size		
							new_item.txt 			= rest if nj>j else cur
							new_item.is_bold 		= self.items[self.idx[ix1]].is_bold 		
							new_item.brightness		= self.items[self.idx[ix1]].brightness		
							new_item.alignment		= self.items[self.idx[ix1]].alignment		
							new_item.font_file		= self.items[self.idx[ix1]].font_file		
							new_item.this_id		= len(self.items)	
							new_item.next_id		= -1	
							new_item.prev_id		= -1
							new_item.category		= self.items[self.idx[ix1]].category		
							new_item.temp_assignment= self.items[self.idx[ix1]].temp_assignment
							new_item.merged_list	= []
							
							old_item_old_width = self.items[self.idx[ix1]].width
							
							self.items[self.idx[ix1]].txt = cur if nj>j else rest
							self.items[self.idx[ix1]].recalc_width()
							new_item.recalc_width()
							
							if(new_item.alignment == ALIGN_RIGHT):
								new_item.pos_x -= new_item.width
								self.items[self.idx[ix1]].pos_x += old_item_old_width  - self.items[self.idx[ix1]].width
							
							self.items.append(new_item)
							self.idx[ix2] = new_item.this_id
					

		# first try our best with strict alignment	
		while(True):
			last_num_items = len(self.items)
			doit(True) 
			if(len(self.items) == last_num_items):
				break
			
		# no be less strict
		while(True):
			last_num_items = len(self.items)
			doit(False) 
			if(len(self.items) == last_num_items):
				break
			
	"""
		
			
	def is_good_table(self):
		neccessary_actual_items = 4 if not config.global_be_more_generous_with_good_tables else 2
		if(not(self.num_rows >= 2 and self.num_cols >= 2 and self.count_actual_items() >= neccessary_actual_items)):
			print_verbose(7, "----->> bad, reason:1")
			return False
			
		num_items  = self.count_actual_items()
		density = num_items / (len(self.idx)+0.00001)
		
		if(density  < 0.2):
			print_verbose(7, "----->> bad, reason:2")
			return False # density less than threshold
		
		num_sp_items = 0
		for sp in self.special_idx:
			if(self.items[sp].txt != ''):
				num_sp_items += 1
		
		if(num_sp_items > num_items * 0.33 and num_items > 50):
			print_verbose(7, "----->> bad, reason:4")
			return False # strange: too many sp. items => probably not a table
			
		cnt_numerics = 0
		cnt_weak_numerics = 0
		for i in self.idx:
			if(i != -1):
				txt = self.items[i].txt
				if(Format_Analyzer.looks_numeric(txt) and not Format_Analyzer.looks_year(txt)):
					cnt_numerics += 1
					cnt_weak_numerics += 1
				elif(Format_Analyzer.looks_weak_numeric(txt)):
					cnt_weak_numerics +=1
					
		print_verbose(7, "----->> reached end of is_good_table")
		return (cnt_numerics > 3 and density > 0.6) or (cnt_numerics > 7 and density > 0.4) or cnt_numerics > 10 \
		    or (cnt_weak_numerics > 3 and num_items > 5 and density > 0.4) \
		    or (cnt_weak_numerics > 0 and num_items > 2 and density > 0.4 and config.global_be_more_generous_with_good_tables)
		
	
	def categorize_as_table(self):
		print_verbose(7, "--> Categorize as new table: "+str(self))
		for i in self.idx:
			if(i!=-1):
				self.items[i].category = CAT_TABLE_DATA
		for i in self.headline_idx:
			if(i!=-1):
				self.items[i].category = CAT_TABLE_HEADLINE
		for i in self.special_idx:
			if(i!=-1):
				self.items[i].category = CAT_TABLE_SPECIAL
			
		
	def categorize_as_misc(self):
		print_verbose(7, "--> Categorize as misc: "+str(self))
		for i in self.get_all_idx():
			if(i!=-1):
				self.items[i].category = CAT_MISC
			
		
	
	def init_by_cols(self, p_idx, p_items):

		self.items = p_items
		self.idx = p_idx.copy()
		self.idx = sorted(self.idx, key=lambda i: self.items[i].pos_y)
		
		self.num_cols = 1
		self.num_rows = len(self.idx)
		
		sum_align_pos_x = 0
		
		for i in self.idx:
			#self.rows.append(self.items[i].get_rect())
			self.marks.append(0)
			sum_align_pos_x += self.items[i].get_aligned_pos_x()
		
		self.col_aligned_pos_x.append(sum_align_pos_x / len(self.idx))
		
		"""
		col_rect = Rect(9999999, 9999999, -1, -1)
		for r in self.rows:
			col_rect.x0 = min(col_rect.x0, r.x0)
			col_rect.y0 = min(col_rect.y0, r.y0)
			col_rect.x1 = max(col_rect.x1, r.x1)
			col_rect.y1 = max(col_rect.y1, r.y1)
			
		self.cols.append(col_rect)
		"""
		
		self.recalc_geometry()
		
	def find_top_marked_idx(self, mark):
		res = -1
		pos_y = 9999999
		for i in range(len(self.idx)):
			if(self.has_item_at_ix(i)):
				cur_y = self.get_item_by_ix(i).pos_y
				if(cur_y < pos_y and self.marks[i] == mark):
					pos_y = cur_y
					res = i
		return res	
		
	def find_left_marked_idx(self, mark):
		res = -1
		pos_x = 9999999
		for i in range(len(self.idx)):
			if(self.has_item_at_ix(i)):
				cur_x = self.get_item_by_ix(i).pos_x
				if(cur_x < pos_x and self.marks[i] == mark):
					pos_x = cur_x
					res = i
		return res	
		
			
				
	def find_marked_idx_at_y0(self, mark, id, y0, new_mark):
		res = []
		for i in range(len(self.idx)):
			if(self.has_item_at_ix(i) and self.marks[i] == mark):
				if(self.get_item_by_ix(i).pos_y == y0):
					res.append((id, i))
					self.marks[i] = new_mark
		return res
		
	def find_marked_idx_between_y0_y1_at_col(self, mark, id, y0, y1, col, new_mark):
		res = []
		for i in range(self.num_rows):
			ix = self.get_ix(i, col)
			if(self.has_item_at_ix(ix) and self.marks[ix] == mark):
				r = self.get_item_by_ix(ix).get_rect()
				if(r.y0 < y1 and r.y1 >= y0):
					res.append((id, ix))
					self.marks[ix] = new_mark
		return res		
		
		
			
			
			
	@staticmethod
	def merge(tab1, tab2, page_width): #note: tables must belong to same HTMLPage !
	
		def cols_are_mergable(tab1, tab2, col1, col2):
			c1_x0 = 9999999
			c1_x1 = -1

			c2_x0 = 9999999
			c2_x1 = -1
			
			for i in range(tab1.num_rows):
				c1_x0 = min(c1_x0, tab1.get_item(i, col1).pos_x if tab1.has_item_at(i, col1) else 9999999)
				c1_x1 = max(c1_x1, tab1.get_item(i, col1).pos_x + tab1.get_item(i, col1).width if tab1.has_item_at(i, col1) else -1)
				
			for i in range(tab2.num_rows):
				c2_x0 = min(c2_x0, tab2.get_item(i, col2).pos_x if tab2.has_item_at(i, col2) else 9999999)
				c2_x1 = max(c2_x1, tab2.get_item(i, col2).pos_x + tab2.get_item(i, col2).width if tab2.has_item_at(i, col2) else -1)
				
			#print("MERGE : !!"+str(c1_x0)+" "+str(c1_x1)+" <-> "+str(c2_x0)+" "+str(c2_x1)+" ")
			
			if(c1_x0 < c2_x0):
				if(not c1_x1 > c2_x0):
					return False
			else:
				if(not c2_x1 > c1_x0):
					return False
					
			# make sure that now rows are overlapping
			
			row1 = 0
			row2 = 0
			while(row1 < tab1.num_rows and row2 < tab2.num_rows):
				if(tab1.has_item_at(row1, col1) and tab2.has_item_at(row2, col2)):
					it1 = tab1.get_item(row1, col1)
					it2 = tab2.get_item(row2, col2)
					if(min(it1.pos_y + it1.height, it2.pos_y + it2.height) - max(it1.pos_y, it2.pos_y) >= 0):
						return False # overlap
					if(it1.pos_y + it1.height < it2.pos_y + it2.height):
						row1 += 1
					else:
						row2 += 1
				elif(tab1.has_item_at(row1, col1)):
					row2 += 1
				else:
					row1 += 1
			
			return True # no overlaps found
			
	
		def find_all_new_columns(tab1, tab2, tmp_rows, threshold_px):
			tab1.reset_marks()
			tab2.reset_marks()
			num_rows = len(tmp_rows)
			
			tmp_cols = []
			tab1_col = 0
			tab2_col = 0
			
			while(tab1_col < tab1.num_cols or tab2_col < tab2.num_cols):
				tmp_items = []
				# find leftmost col
				print_verbose(5, "----> tab1_col=" + str(tab1_col) + ", tab2_col=" + str(tab2_col))
				tab1_col_x = tab1.col_aligned_pos_x[tab1_col] if tab1_col < tab1.num_cols else 9999999
				tab2_col_x = tab2.col_aligned_pos_x[tab2_col] if tab2_col < tab2.num_cols else 9999999
				use_tab1 = tab1_col_x <= tab2_col_x + threshold_px
				use_tab2 = tab2_col_x <= tab1_col_x + threshold_px
				if(use_tab1 and use_tab2 and not cols_are_mergable(tab1, tab2, tab1_col, tab2_col)): # TODO: and cols do not intersect by any rect
					# cols cant be merged => use only first one
					use_tab1 = tab1_col_x < tab2_col_x
					use_tab2 = not use_tab1			

				print_verbose(5, "------> tab1_col_x=" + str(tab1_col_x) + ", tab2_col_x=" + str(tab2_col_x)+ ", use1/2="+str(use_tab1)+"/"+str(use_tab2))

				
				# insert items from that col(s)
				for i in range(num_rows):
					y0 = tmp_rows[i]
					y1 = tmp_rows[i+1] if i < num_rows - 1 else 9999999
					
					list_idx = []
					if(use_tab1):
						list_idx += tab1.find_marked_idx_between_y0_y1_at_col(0, 1, y0, y1, tab1_col, 1)
					if(use_tab2):
						list_idx += tab2.find_marked_idx_between_y0_y1_at_col(0, 2, y0, y1, tab2_col, 1)
				
					if(len(list_idx) > 1):
						list_idx = sorted(list_idx, key=lambda id_i: tab1.items[tab1.idx[id_i[1]]].pos_y if id_i[0] == 1 else tab2.items[tab2.idx[id_i[1]]].pos_y )
						for k in range(len(list_idx)-1):
							id, ix = list_idx[k]
							id1, ix1 = list_idx[k+1]
							it = tab1.items[tab1.idx[ix]] if id == 1 else tab2.items[tab2.idx[ix]]
							it1 = tab1.items[tab1.idx[ix1]] if id1 == 1 else tab2.items[tab2.idx[ix1]]
							if(not it.is_mergable(it1)):
								#we found two items, that can't be merged => split row, and try again
								if(it.pos_y == it1.pos_y):
									#very strange case! should normally never occurence. bad can happen due to bad pdf formatting
									print_verbose(6, "------>>> Bad case! Must rearrange item")
									it1.pos_y += it1.height * 0.0001
								print_verbose(5, "-----> Split neccessary: " + str(it) + " cant be merged with " +str(it1))
								print_verbose(5, "-----> Split is here: " + str(tmp_rows[0:i+1]) +" <-> " +str(it1.pos_y) + " <-> "+ str(tmp_rows[i+1:]))
								tmp_rows = tmp_rows[0:i+1] + [it1.pos_y] + tmp_rows[i+1:]
								return False, [], tmp_rows
						
						#everything can be merged => merge
						for k in range(len(list_idx)-1, 0, -1):
							id, ix = list_idx[k]
							id1, ix1 = list_idx[k-1]
							it = tab1.items[tab1.idx[ix]] if id == 1 else tab2.items[tab2.idx[ix]]
							it1 = tab1.items[tab1.idx[ix1]] if id1 == 1 else tab2.items[tab2.idx[ix1]]		
							it1.merge(it)
					
					if(len(list_idx) == 0):
						tmp_items.append(-1)
					else:	
						id, ix = list_idx[0]
						tmp_items.append(tab1.idx[ix] if id == 1 else tab2.idx[ix])
				
				tmp_cols.append(tmp_items)
				
				#  continue with next col
				if(use_tab1):
					tab1_col += 1
				if(use_tab2):
					tab2_col += 1
					

			return True, tmp_cols, tmp_rows


				
	
		if(tab1.items != tab2.items):
			raise ValueError('tab1 and tab2 belong to different HTMLPages')

		tmp_idx = tab1.idx + tab2.idx
		tmp_idx = list(filter(lambda ix: ix != -1, tmp_idx))
		if(len(tmp_idx) != len(set(tmp_idx))):
			raise ValueError('tab1 '+str(tab1.idx)+' and tab2 '+str(tab2.idx)+' intersect')
		
		# Find all new rows
		print_verbose(5, "--> Finding rows")
		tab1.reset_marks()
		tab2.reset_marks()
		
		tmp_rows = []
		
		threshold_px = DEFAULT_VTHRESHOLD * page_width
		
		while(tab1.count_marks(0) > 0 or tab2.count_marks(0) > 0):
			idx1 = tab1.find_top_marked_idx(0)
			idx2 = tab2.find_top_marked_idx(0)
			if(idx1 == -1 and idx2 ==-1):
				#strange! this should never happen!
				raise ValueError('idx1 and idx2 are both -1, but marks=0 exist!')
				
			if(idx2 == -1 or (idx1 != -1 and tab1.get_item_by_ix(idx1).pos_y<tab2.get_item_by_ix(idx2).pos_y)):
				cur_rect = tab1.get_item_by_ix(idx1).get_rect()
			else:
				cur_rect = tab2.get_item_by_ix(idx2).get_rect()
				
			list_idx = tab1.find_marked_idx_at_y0(0, 1, cur_rect.y0, 1)
			list_idx += tab2.find_marked_idx_at_y0(0, 2, cur_rect.y0, 1)

			print_verbose(9, "----> Continue with idx1="+str(idx1)+",idx2="+str(idx2)+", r="+str(cur_rect)+", list_idx="+str(list_idx))
			
			
			min_y = 9999999
			for (id, i) in list_idx:
				cur_y = tab1.items[tab1.idx[i]].pos_y if id == 1 else tab2.items[tab2.idx[i]].pos_y
				if(cur_y < min_y):
					min_y = cur_y
			tmp_rows.append(min_y) #(list_idx, min_y))
		
		
		print_verbose(5, "----> Rows: "+ str(tmp_rows))
		# Find all new columns
		print_verbose(3, "--> Rows found, continuing with columns")
		finding_cols_done = False
		tmp_cols = []
		while(not finding_cols_done):
			print_verbose(7, "--> Next try")
			finding_cols_done, tmp_cols, tmp_rows = find_all_new_columns(tab1, tab2, tmp_rows, threshold_px)
			print_verbose(7, "----> New Rows: "+ str(tmp_rows))
			
		# Build resulting table
		print_verbose(3, "--> Columns found, now build final table")

		res = HTMLTable()
		

		res.items = tab1.items
		res.num_rows = len(tmp_rows)
		res.num_cols = len(tmp_cols)
		res.idx = [-1] * (res.num_rows * res.num_cols)
		res.marks = [0] * (res.num_rows * res.num_cols)
		
		for j in range(res.num_cols):
			for i in range(res.num_rows):
				res.idx[i * res.num_cols + j] = tmp_cols[j][i]
		
		res.recalc_geometry()
		
		for it in tab1.items:
			it.recalc_geometry()
		
		return res
	
	
	#TODO: Remove:
	"""
	def get_printed_repr(self):
		COL_WIDTH = 10
		
		res = '*' * (COL_WIDTH * self.num_cols+1) + '\n' # headline
		for i in range(self.num_rows):
			for j in range(self.num_cols):
				if(self.has_item_at(i,j)):
					res += '*'+ str(self.get_item(i, j).txt)[:(COL_WIDTH-1)].ljust(COL_WIDTH-1, ' ')
				else:
					res += '*' + ' '.ljust(COL_WIDTH-1, ' ')
			res += '*\n'+'*' * (COL_WIDTH * self.num_cols+1) + '\n' # headline
		
		return res
	"""
	
	def is_compatible_with_existing_row(self, r0, it0):
		min_y0 = 9999999
		max_y1 = -1
		max_height = 0
		for j in range(self.num_cols):
			if(self.has_non_empty_item_at(r0, j)):
				it = self.get_item(r0, j)
				min_y0 = min(min_y0, it.pos_y)
				max_y1 = max(max_y1, it.pos_y + it.height)
				max_height = max(max_height, it.height)
		
		y0 = it0.pos_y
		y1 = it0.pos_y + it0.height
		if(y1 < min_y0):
			return min_y0 - y1 < 0.5 * max_height
		if(y0 > max_y1):
			return y0 - max_y1 < 0.5 * max_height
		return True
		

	def force_special_items_into_table(self):
		new_special_idx = []
		for idx in self.special_idx:
			ix = self.find_nearest_cell_ix(self.items[idx])
			r, c = self.get_row_and_col_by_ix(ix)
			if(not(self.has_non_empty_item_at(r, c)) and self.is_compatible_with_existing_row(r, self.items[idx])):
				#free cell
				self.idx[ix] = idx
			else:
				#no free cell. can we insert a new row?
				if(self.is_row_insertion_possible(r, self.items[idx].pos_y)):
					self.insert_row(r)
					self.idx[self.get_ix(r+1, c)] = idx
					self.recalc_geometry()
				else:
					#no empty space. leave as special item
					new_special_idx.append(idx)
		self.special_idx = new_special_idx
		
		self.recalc_geometry()
		self.compactify()
			
			
		
	def is_non_overlapping_row_mergable(self, r0): # return True iff row r0 and r0+1 can be merged
		if(r0 < 0 or r0 >= self.num_rows - 1):
			raise ValueError('Rows r0='+str(r0)+' and r0+1 out of range.')
			
			
		# only one row is allowed to contain numbers
		n0 = False
		n1 = False
		for j in range(self.num_cols):
			if(self.has_item_at(r0,j) and Format_Analyzer.looks_numeric(self.get_item(r0,j).txt)):
				n0 = True
			if(self.has_item_at(r0+1,j) and Format_Analyzer.looks_numeric(self.get_item(r0+1,j).txt)):
				n1 = True
	
		if(n0 and n1):
			print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1 have both numbers')
			return False,0 # both rows contain numbers			
		
		#if(config.global_table_merging_only_if_numbers_come_first and not n0):
		#	print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1, the first one has no numbers.')
		#	return False,0 # 
			
			
		y0_max = 0
		y1_min = 9999999
		
		has_mergable_candidates = False
		font_chars = ""
		for j in range(self.num_cols):
			both_filled = self.has_item_at(r0, j) and self.has_item_at(r0+1, j) 
			if(both_filled and not self.get_item(r0,j).is_weakly_mergable_after_reconnect(self.get_item(r0+1,j))):
				print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1 are not mergable. Items:' \
				                  + str(self.get_item(r0,j)) + ' and ' + str(self.get_item(r0+1,j)))
				return False,0
			if(both_filled):
				has_mergable_candidates = True
				font_chars = self.get_item(r0,j).get_font_characteristics()
				if(self.get_item(r0,j).pos_y + self.get_item(r0,j).height*(3.0 if n0 else 2.1) < self.get_item(r0+1,j).pos_y):
					print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1 are too far apart. Items:' \
					                  + str(self.get_item(r0,j)) + ' and ' + str(self.get_item(r0+1,j)))
					return False,0
				cur_y0 = self.get_item(r0, j).pos_y + self.get_item(r0, j).height if self.has_item_at(r0, j) else 0
				cur_y1 = self.get_item(r0+1, j).pos_y if self.has_item_at(r0+1, j) else 9999999
				y0_max = max(y0_max, cur_y0)
				y1_min = min(y1_min, cur_y1)

		if(not has_mergable_candidates):
			print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1 have no mergable candidates')
			return False,0

		if(y0_max >= y1_min):
			print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1 would overlap')
			return False,0
			
		# make sure, all same font characteristics
		for j in range(self.num_cols):
			if((self.has_item_at(r0, j) and self.get_item(r0,j).get_font_characteristics() != font_chars) \
			   or (self.has_item_at(r0+1, j) and self.get_item(r0+1,j).get_font_characteristics() != font_chars)):
				print_verbose(8, '--->> is_non_overlapping_row_mergable: Rows r0='+str(r0)+' and r0+1 have different font chars')
				return False,0
			
		mod_dist = math.floor((y1_min-y0_max)*100.0)/100.0 * (0.66 if n0 else 1)
		print_verbose(8, "---->>> For row="+str(r0)+", mod_dist="+str(mod_dist) + ", y0_max=" +str(y0_max) + ",y1_min="+str(y1_min))
		return True, mod_dist # TODO: maybe use only the distance, where both rows are filled?
	
	
		
	def merge_non_overlapping_rows_single(self):
		# this will merge rows, even if both them contain text, by appending the text
		merge_list = []
		min_dist = 9999999
		min_row = -1
		for i in range(self.num_rows-1):
			is_merg, dist = self.is_non_overlapping_row_mergable(i)
			if(is_merg):
				merge_list.append(i)
				if(dist<min_dist):
					min_dist = min(min_dist, dist)
					min_row = i
		
		print_verbose(7, "The following non-overlapping rows could be merged: " + str(merge_list))
		if(len(merge_list)==0):
			return False # nothing was merged
			
		print_verbose(7, "We merge now " + str(min_row))
		
		print_verbose(9, "Before merging: " + self.get_printed_repr())
		self.merge_rows(min_row, True)
		print_verbose(9, "After merging rows " +str(min_row)+" and r+1: " + self.get_printed_repr())
		
		self.recalc_geometry()
		print_verbose(9, "After recalc geometry: " + self.get_printed_repr())
		
		return True #we merged something!
	
	def merge_non_overlapping_rows(self):
		print_verbose(7, "merge_non_overlapping_rows, Table=" + self.get_printed_repr())
		while True:
			if(not self.merge_non_overlapping_rows_single()):
				return
	

	def generate_sub_tables(self): # generates sub-tables that are helpful for the AnalyzerTable, based on year-columns
	
		class YearCols:
			r = None
			c0 = None
			c1 = None
			def __init__(self, r, c0):
				self.r=r
				self.c0=c0
			
			def __repr__(self):
				return "(r="+str(self.r)+",c0="+str(self.c0)+",c1="+str(self.c1)+")"
				
		year_cols = [] 
		

		for i in range(self.num_rows):
			j = 0
			while(j < self.num_cols - 1):
				if(self.has_item_at(i,j) and self.has_item_at(i,j+1) and \
				   Format_Analyzer.looks_year(self.get_item(i,j).txt) and \
				   Format_Analyzer.looks_year(self.get_item(i,j+1).txt) and \
				   abs(Format_Analyzer.to_year(self.get_item(i,j+1).txt) - Format_Analyzer.to_year(self.get_item(i,j).txt)) == 1):
					dir = Format_Analyzer.to_year(self.get_item(i,j+1).txt) - Format_Analyzer.to_year(self.get_item(i,j).txt)
					cur_year_cols = YearCols(i, j)
					#find last year col
					#print("Now at cell:"+str(i)+","+str(j))
					for j1 in range(j+1, self.num_cols):
						if(self.has_item_at(i,j1) and \
						   Format_Analyzer.looks_year(self.get_item(i,j1).txt) and \
						   Format_Analyzer.to_year(self.get_item(i,j1).txt) - Format_Analyzer.to_year(self.get_item(i,j1-1).txt) == dir):
							cur_year_cols.c1 = j1
						else:
							break
					year_cols.append(cur_year_cols)
					j = cur_year_cols.c1
				j += 1
				
		print_verbose(6, '----->> Found year lists at: ' +str(year_cols))
		
		
		yl = []
		for yc in year_cols:
			yl.append((yc.c0, yc.c1))
		
		yl = list(set(yl))
			
		res = []
		for y in yl:
			if(y[0] - 1 > 0):
				cur_tab = deepcopy(self)
				if(y[1]+1 < cur_tab.num_cols):
					cur_tab.delete_cols(y[1]+1, cur_tab.num_cols)
				cur_tab.delete_cols(0, y[0]-1)
				print_verbose(6, "Found sub-table:\n"+str(cur_tab.get_printed_repr()))
				res.append(cur_tab)
			
		return res
	
			
			
			
	def save_to_csv(self, csv_file):
		ctab = ConsoleTable(self.num_cols)
		
		for ix in range(self.num_rows * self.num_cols):
			ctab.cells.append(self.items[self.idx[ix]].txt if self.has_item_at_ix(ix) else '')

		res = ctab.to_string(use_format = ConsoleTable.FORMAT_CSV)		

		save_txt_to_file(res, csv_file)
			
			
			
		
	def get_printed_repr(self):
		COL_WIDTH = 10
		
		special_printed = [False] * len(self.special_idx)
		
		res = '' 
		# table headline title
		for i in self.headline_idx:
			res += '===> ' + self.items[i].txt + '<===\n'
			
		
		# headline
		res += '\u2554'
		for j in range(self.num_cols):
			res += '\u2550' * (COL_WIDTH-1)
			res += '\u2566' if j < self.num_cols - 1 else '\u2557\n'
			
		# content
		for i in range(self.num_rows):
			# frame line
			if(i>0):
				res += '\u2560'
				for j in range(self.num_cols):
					res += '\u2550'*(COL_WIDTH-1)
					res += '\u256c' if j < self.num_cols -1 else '\u2563'
				res += '\n'
			
			# content line
			res += '\u2551'
			for j in range(self.num_cols):
				if(self.has_item_at(i,j)):
					txt = self.get_item(i, j).txt.replace('\n', ' ')
					res += str(txt)[:(COL_WIDTH-1)].ljust(COL_WIDTH-1, ' ')
				else:
					res +=' '.ljust(COL_WIDTH-1, ' ')
				res += '\u2551'
				
			# special items
			sp_ix = self.find_applying_special_item_ix(i)
			if(sp_ix is not None and special_printed[sp_ix] == False):
				special_printed[sp_ix] = True
				res += ' * ' + self.items[self.special_idx[sp_ix]].txt[:COL_WIDTH]
				
			
				
			res += '\n'
			
		# footer line
		res += '\u255a'
		for j in range(self.num_cols):
			res += '\u2550' * (COL_WIDTH-1)
			res += '\u2569' if j < self.num_cols - 1 else '\u255d\n'
			
	
		
		return res
		
		
		
			
	def __repr__(self):
		res = 'Row-Dim: ' + str(self.rows)
		res += '\nCol-Dim: ' +str(self.cols)
		res	+= '\nSpecial-Items: '
		for k in self.special_idx:
			res += str(self.items[k]) + ' '
		res += '\n' + self.get_printed_repr()
		return res
	

	
	
	
	
	

