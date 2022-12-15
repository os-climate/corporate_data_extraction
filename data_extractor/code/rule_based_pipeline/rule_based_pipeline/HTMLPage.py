# ============================================================================================================================
# PDF_Analyzer
# File   : HTMLPage.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 HTMLPage consistens of * HTMLItems
# Note   : 1 HTMLPage consistens of * HTMLTables
# Note   : 1 HTMLPage consistens of * HTMLCluster
# Note   : 1 HTMLDirectory consistens of * HTMLPages
# ============================================================================================================================

from globals import *
from HTMLTable import *
from HTMLCluster import *
import copy
		

class HTMLPage:
	page_num 		= None
	page_width		= None
	page_height		= None
	items			= None
	left_distrib	= None #distribution of pos_x values (left alignments)
	tables			= None
	paragraphs		= None
	clusters		= None
	clusters_text	= None #clusters for traversing raw text
	footnotes_idx	= None
	page_start_y0	= None
	
	def __init__(self):
		self.page_num 		= 0
		self.page_width 	= 0
		self.page_height 	= 0
		self.items			= []
		self.left_distrib	= {}
		self.tables			= []
		self.paragraphs 	= []
		self.clusters		= []
		self.clusters_text	= []
		self.footnotes_idx	= []
		self.page_start_y0 	= [0]
	
	
	# =====================================================================================================================
	# Utilities for Handling Multiple pages
	# =====================================================================================================================		
	
	
	@staticmethod
	def merge(p0, p1): # merge two pages (p1 will be below p0)
		def get_max_line_num(p):
			res = 0
			for it in p.items:
				if(it.line_num > res):
					res = it.line_num
			return res
			
		def get_max_id(p):
			res = -1
			for it in p.items:
				if(it.this_id > res):
					res = it.this_id
			return res
			
		def transform_id(id, offset):
			if(id==-1):
				return -1
			return id + offset
			
		p0c = copy.deepcopy(p0) #p0's copy
		p1c = copy.deepcopy(p1) #p1's copy
		#p0c will be the result
		p0c.page_start_y0.append(p0c.page_height)
		p0c.page_height += p1c.page_height
		p0c.page_width = max(p0c.page_width, p1c.page_width)
		p1c_min_line_num = get_max_line_num(p0c) + 1
		p1c_min_id = get_max_id(p0c) + 1
		p0c_num_items = len(p0c.items)
		
		for it in p1c.items:
			it.line_num += p1c_min_line_num
			it.tot_line_num = p0c.page_num * 10000 + it.line_num
			it.pos_y += p1c.page_height
			it.this_id = transform_id(it.this_id, p1c_min_id)
			it.next_id = transform_id(it.next_id, p1c_min_id)
			it.prev_id = transform_id(it.prev_id, p1c_min_id)
			it.left_id = transform_id(it.left_id, p1c_min_id)
			it.right_id = transform_id(it.right_id, p1c_min_id)
			it.merged_list = [transform_id(id, p1c_min_id) for id in it.merged_list]
			for w in it.words:
				w.item_id = transform_id(w.item_id, p1c_min_id)
				w.rect.y0 += p0c.page_height
				w.rect.y1 += p0c.page_height
			#print(it)
			p0c.items.append(it)
		
		for ky in p1c.left_distrib:
			p0c.left_distrib[ky] = p0c.left_distrib.get(ky, 0) + p1c.left_distrib[ky]
		
		for t in p1c.tables:
			t.recalc_geometry()
		
		p0c.tables.extend(p1c.tables)
		p0c.find_paragraphs()
		
		for idx in p1c.footnotes_idx:
			p0c.footnotes_idx.append(idx + p0c_num_items)
		
		p0c.generate_clusters()
		
		return p0c
		
		
	
	
	# =====================================================================================================================
	# Utilities for Identifying Basic Structures
	# =====================================================================================================================		
	
	# transform coordinates such that they are in [0,1) range on the current page
	def transform_coords(self, x, y):
		#print("TTTT")
		#print(str(x) + "," + str(y) + "-> " + str(self.page_width) + ", " + str(self.page_start_y0) + ", " + str(self.page_height))
		res_x = x / self.page_width
		res_y = 1
		for i in range(len(self.page_start_y0)):
			start_y = self.page_start_y0[i]
			end_y = self.page_start_y0[i+1] if i < len(self.page_start_y0)-1 else self.page_height
			res_y = (y-start_y)/(end_y-start_y)
			if(res_y<1):
				break
		return res_x, res_y
	
	def find_idx_of_item_by_txt(self, txt):
		res = -1
		for i in range(len(self.items)):
			if(self.items[i].txt == txt):
				if(res != -1):
					raise ValueError('Text "'+txt+'" occurs more than once in this page.')
				res = i
		return res
		
	def detect_split_items(self):
	
		def find_aligned_words_in_direction(all_words, k0, use_alignment, dir):
			SPLIT_DETECTION_THRESHOLD = 1.0 / 609.0
			
			threshold = SPLIT_DETECTION_THRESHOLD * self.page_width
			
			item_id0 = all_words[k0][0]
			word_id0 = all_words[k0][1]
			x0_0 = self.items[item_id0].words[word_id0].rect.x0
			x1_0 = self.items[item_id0].words[word_id0].rect.x1
			
			k_max = len(all_words)
			k = k0 + dir
			res = []
			is_numeric = False
			while(0<= k and k < k_max):
				item_id = all_words[k][0]
				word_id = all_words[k][1]
				x0 = self.items[item_id].words[word_id].rect.x0
				x1 = self.items[item_id].words[word_id].rect.x1
				
				if(use_alignment == ALIGN_LEFT and abs(x0-x0_0) < threshold):
					# we found a left-aligned word
					res.append(k)
					is_numeric = is_numeric or Format_Analyzer.looks_weak_numeric(self.items[item_id].words[word_id].txt)
				elif(use_alignment == ALIGN_RIGHT and abs(x1-x1_0) < threshold):
					# we found a right-aligned word
					res.append(k)
					is_numeric = is_numeric or Format_Analyzer.looks_weak_numeric(self.items[item_id].words[word_id].txt)
				#elif(x0 < x1_0 and x1 > x0_0):
				elif((x0 < x0_0 and x1 > x0_0 and use_alignment == ALIGN_LEFT) or (x0 < x1_0 and x1 > x1_0 and use_alignment == ALIGN_RIGHT)):
					#print('BAD:'+self.items[item_id].words[word_id].txt)
					#print(x0, x0_0, threshold)
					break # another word is in the way, but not correctly aligned

				k += dir
			return res, is_numeric
			
		def find_space_in_direction(all_words, k0, dir):
			item_id = all_words[k0][0]
			word_id = all_words[k0][1]
			num_words = len(self.items[item_id].words)			
			if(dir==-1):
				return self.items[item_id].words[word_id].rect.x0 - self.items[item_id].words[word_id-1].rect.x1 if word_id > 0 else 9999999
			elif(dir==1):
				return self.items[item_id].words[word_id+1].rect.x0 - self.items[item_id].words[word_id].rect.x1 if word_id < num_words-1 else 9999999
			raise ValueError('Invalid dir')
			return -1 # should never happen
			
			
		# prepare sorted order of all words
		all_words = []
		
		for i in range(len(self.items)):
			for j in range(len(self.items[i].words)):
				all_words.append((i, j, False))
			
		all_words = sorted(all_words, key=lambda ij: self.items[ij[0]].words[ij[1]].rect.y0)
		
		do_split_l = []
		do_split_r = []
		
		
		# find words that can be split
		for k in range(len(all_words)):
			item_id = all_words[k][0]
			word_id = all_words[k][1]
			num_words = len(self.items[item_id].words)
			
			isnum = Format_Analyzer.looks_weak_numeric(self.items[item_id].words[word_id].txt)
			isnum_l = Format_Analyzer.looks_weak_numeric(self.items[item_id].words[word_id-1].txt) if word_id > 0 else False
			isnum_r = Format_Analyzer.looks_weak_numeric(self.items[item_id].words[word_id+1].txt) if word_id < num_words-1 else False
			
			# left-aligned words:
			#print("L")
			left_aligned_words_down, isnum_ld = find_aligned_words_in_direction(all_words, k, ALIGN_LEFT, 1) 
			left_aligned_words_up, isnum_lu = find_aligned_words_in_direction(all_words, k, ALIGN_LEFT, -1) 
			left_aligned_words = left_aligned_words_down + left_aligned_words_up
			
			
			# right-aligned words:
			#print("R")
			right_aligned_words_down, isnum_rd = find_aligned_words_in_direction(all_words, k, ALIGN_RIGHT, 1)
			right_aligned_words_up, isnum_ru = find_aligned_words_in_direction(all_words, k, ALIGN_RIGHT, -1)
			right_aligned_words = right_aligned_words_down + right_aligned_words_up
			
			
			# It doesnt make sense to split for CENTER aligned words # New-27.06.2022
			
			isnum_l = isnum_l or isnum_ld or isnum_lu
			isnum_r = isnum_r or isnum_rd or isnum_ru

			
			threshold_rows_l = 1 if isnum and isnum_l else 2
			threshold_rows_r = 1 if isnum and isnum_r else 2
			
			threshold_space_l = (1.2 if isnum and isnum_l else 1.5) * self.items[item_id].space_width
			threshold_space_r = (1.2 if isnum and isnum_r else 1.5) * self.items[item_id].space_width			
			
			# space between this and previous/next word
			space_width_l = find_space_in_direction(all_words, k, -1)
			space_width_r = find_space_in_direction(all_words, k, 1)
			
			"""
			space_width_l_min = space_width_l
			for n in left_aligned_words:
				space_width_l_min = min(space_width_l_min, find_space_in_direction(all_words, n, -1))
			
			space_width_r_min = space_width_r
			for n in right_aligned_words:
				space_width_r_min = min(space_width_r_min, find_space_in_direction(all_words, n, 1))
			"""

			#if(self.items[item_id].words[word_id].txt=='2019-2q'):
			#	print(self.items[item_id].words[word_id].txt)
			#	print(len(left_aligned_words) , threshold_rows_l , word_id , num_words, space_width_l_min , threshold_space_l)
			#	print(len(right_aligned_words) , threshold_rows_r , word_id , num_words, space_width_r_min , threshold_space_r)
			
			
			#if(len(left_aligned_words) > threshold_rows_l and word_id > 0 and space_width_l_min > threshold_space_l):
			if(len(left_aligned_words) > threshold_rows_l and word_id > 0 and space_width_l > threshold_space_l):
				#print(self.items[item_id].words[word_id].txt)
				do_split_l.append(k)
				#do_split.extend(left_aligned_words)
				
			#if(len(right_aligned_words) > threshold_rows_r and word_id < num_words-1 and space_width_r_min > threshold_space_r):
			if(len(right_aligned_words) > threshold_rows_r and word_id < num_words-1 and space_width_r > threshold_space_r):
				#print(self.items[item_id].words[word_id].txt)
				#print('!!!')
				do_split_r.append(k)
				#do_split.extend(right_aligned_words)
				

			if(space_width_l > 3 * self.items[item_id].space_width and word_id > 0 ):
				# two words are are too far apart => split them in any case
				do_split_l.append(k)
				do_split_l.extend(left_aligned_words)
				

			if(space_width_r > 3 * self.items[item_id].space_width and word_id < num_words-1 ):
				# two words are are too far apart => split them in any case
				do_split_r.append(k)
				do_split_r.extend(right_aligned_words)	
				#print('!!!!!!!')

				
			#print('???')

			

		# do splitting
		for k in do_split_l:
			if(all_words[k][1] > 0):
				all_words[k] = (all_words[k][0], all_words[k][1], True)

		word_map = {}
		for k in range(len(all_words)):
			word_map[(all_words[k][0],all_words[k][1])] = k
	
			
		for k in do_split_r:
			item_id = all_words[k][0]
			word_id = all_words[k][1]
			num_words = len(self.items[item_id].words)
			if(word_id < num_words-1):
				kr = word_map[(item_id, word_id+1)]
				all_words[kr] = (all_words[kr][0], all_words[kr][1], True)
				
		all_words = sorted(all_words, key=lambda ij: -ij[1]) #split always beginning from the end
		
		next_id = len(self.items)
		
		for ij in all_words:
			if(not ij[2]):
				continue # do not split this one
			if(self.items[ij[0]].words[ij[1]].rect.x0 - self.items[ij[0]].words[ij[1]-1].rect.x1 < self.items[item_id].space_width * 0):
				continue # words are too close to split

			if(self.items[ij[0]].words[ij[1]].rect.x0 - self.items[ij[0]].words[ij[1]-1].rect.x1 < self.items[item_id].space_width * 1.5 and \
			   not Format_Analyzer.looks_weak_numeric(self.items[ij[0]].words[ij[1]].txt) and \
			   not Format_Analyzer.looks_weak_numeric(self.items[ij[0]].words[ij[1]-1].txt)):
				continue # words are too close to split
				
			
			
			print_verbose(3, '---> Split item '+str(self.items[ij[0]]) + ' at word ' + \
			   str(ij[1]) + '(x1='+str(self.items[ij[0]].words[ij[1]-1].rect.x1)+'<-> x0='+str(self.items[ij[0]].words[ij[1]].rect.x0)+ \
			   ' , space_width= '+str(self.items[item_id].space_width))
			new_item = self.items[ij[0]].split(ij[1], next_id)
			self.items.append(new_item)
			print_verbose(3, '------> Result = "'+str(self.items[ij[0]].txt) + '" + "' + str(new_item.txt) + '"')

			next_id += 1
				
		
		
			
		#raise ValueError('XXX')
		
		
		
	def get_txt_unsplit(self, idx):
		if(self.items[idx].right_id==-1):
			return self.items[idx].txt
		return self.items[idx].txt  + " " + self.get_txt_unsplit(self.items[idx].right_id)

	
		
		
	def find_left_distributions(self):
		self.left_distrib	= {}
		for it in self.items:
			cur_x = it.pos_x
			self.left_distrib[cur_x] = self.left_distrib.get(cur_x, 0) + 1
		print_verbose(5, 'Left distrib: ' + str(self.left_distrib))
		
	def find_paragraphs(self):
		self.paragraphs = []
		
		distrib = {}
		for it in self.items:
			if(it.category == CAT_RUNNING_TEXT or it.category == CAT_HEADLINE):
				cur_x = it.pos_x
				distrib[cur_x] = distrib.get(cur_x, 0) + 1
		
		for pos_x, frequency in distrib.items():
			if(frequency > 5):
				self.paragraphs.append(pos_x)
				
		self.paragraphs.sort()
		
	
	def find_items_within_rect_all_categories(self, rect): # returns list of indices
		res = []
		for i in range(len(self.items)):
			if(Rect.calc_intersection_area(self.items[i].get_rect(), rect) > self.items[i].get_rect().get_area() * 0.3): #0.5?
				res.append(i)
		return res
		
	def find_items_within_rect(self, rect, categories): # returns list of indices
		res = []
		for i in range(len(self.items)):
			if(self.items[i].category in categories):
				if(Rect.calc_intersection_area(self.items[i].get_rect(), rect) > self.items[i].get_rect().get_area() * 0.3): #0.5?
					res.append(i)
		return res
		
	def explode_item(self, idx, sep = ' '): #return concatenated txt
		def expl_int(dir, idx, sep):
			return ('' if self.items[idx].left_id == -1 or dir > 0 else expl_int(-1, self.items[idx].left_id, sep) + sep) + \
			       self.items[idx].txt + \
				   ('' if self.items[idx].right_id == -1 or dir < 0 else sep + expl_int(1, self.items[idx].right_id, sep) )
		return expl_int(0, idx, sep)
				
	
	def explode_item_by_idx(self, idx): #return list of idx
		def expl_int(dir, idx):
			return ([] if self.items[idx].left_id == -1 or dir > 0 else expl_int(-1, self.items[idx].left_id)) + \
			       [idx]+ \
				   ([] if self.items[idx].right_id == -1 or dir < 0 else expl_int(1, self.items[idx].right_id) )
		return expl_int(0, idx)		
		
	def find_vertical_aligned_items(self, item, alignment, threshold, do_print=False): #TODO: remove do_print
		#returns indices of affected items
		res = []

		if(alignment != ALIGN_DEFAULT):
			this_align = alignment
		else:
			this_align = item.alignment

		pos_x = item.pos_x
		pos_y = item.pos_y
		threshold_px = threshold * self.page_width
		
		score = 0.0
		
		if(this_align == ALIGN_RIGHT):
			pos_x += item.width
		# New-27.06.2022:
		if(this_align == ALIGN_CENTER):
			pos_x += item.width*0.5

			
		for i in range(len(self.items)):
			if(alignment != ALIGN_DEFAULT):
				cur_align = alignment
			else:
				cur_align = self.items[i].alignment
			cur_x = self.items[i].pos_x
			cur_y = self.items[i].pos_y
			
			if(cur_align == ALIGN_RIGHT):
				cur_x += self.items[i].width
			if(cur_align == ALIGN_CENTER):
				cur_x += self.items[i].width*0.5

				
			delta = abs(cur_x-pos_x)
			if(do_print):
				print_verbose(7, '---> delta for '+str(self.items[i])+' to '+str(pos_x)+' is '+str(delta))
			if(delta <= threshold_px):
				cur_score = ((threshold_px - delta)/self.page_width) * ( ((1.0 - abs(cur_y - pos_y) / self.page_height)) ** 5.0) 
				if(cur_score<0.003):
					cur_score=0
				print_verbose(9, "VALIGN->"+str(self.items[i])+" has SCORE: "+str(cur_score))
				score += cur_score
				res.append(i)
			
		return res, score
		
		
		
	
	def find_horizontal_aligned_items(self, item):
		#returns indices of affected items
		res = []
		
		y0 = item.pos_y
		y1 = item.pos_y + item.height 
		
		for i in range(len(self.items)):
			it = self.items[i]
			if(it.pos_y < y1 and it.pos_y + it.height > y0):
				res.append(i)
				
		return res
		
		
	def clear_all_temp_assignments(self):
		for it in self.items:
			it.temp_assignment = 0
		
	def guess_all_alignments(self):
		for it in self.items:
			dummy, score_left = self.find_vertical_aligned_items(it, ALIGN_LEFT, DEFAULT_VTHRESHOLD)
			dummy, score_right = self.find_vertical_aligned_items(it, ALIGN_RIGHT, DEFAULT_VTHRESHOLD)
			dummy, score_center = self.find_vertical_aligned_items(it, ALIGN_CENTER, DEFAULT_VTHRESHOLD) # New-27.06.2022
			#it.alignment = ALIGN_LEFT if score_left >= score_right else ALIGN_RIGHT
			if(score_left >= score_right and score_left >= score_center):
				it.alignment = ALIGN_LEFT
			elif(score_right >= score_left and score_right >= score_center):
				it.alignment = ALIGN_RIGHT
			else:
				it.alignment = ALIGN_CENTER
			
			
	def find_next_nonclassified_item(self):
		for it in self.items:
			if(not it.has_category()):
				return it
		return None
		
			
	def identify_connected_txt_lines(self):
	
		def insert_next_id(cur_id, next_id, items):
			if(items[next_id].pos_y <= items[cur_id].pos_y):
				raise ValueError('Invalid item order:' + str(items[cur_id]) + ' --> ' +str(items[next_id]))

					
			if(items[cur_id].next_id==-1):
				items[cur_id].next_id = next_id
			elif(items[cur_id].next_id==next_id):
				return
			else:
				old_next_id = items[cur_id].next_id
				if(items[next_id].pos_y < items[old_next_id].pos_y):
					items[cur_id].next_id = next_id
					insert_next_id(next_id, old_next_id, items)
				elif(items[next_id].pos_y < items[old_next_id].pos_y):
					insert_next_id(old_next_id, next_id, items)
				else:
					# sometimes this can happen, but then we dont update anything in order to avoid cycles
					pass
	

		threshold = int(0.03 * self.page_width + 0.5) # allow max 3% deviation to the left
		cur_threshold = 0
	
		for cur_x, cnt in self.left_distrib.items():
			if(cnt < 2):
				# if we have less than 2 lines, we skip this "column"
				continue
				
			cur_lines = {} # for each line in this column, we store its y position
			last_pos_y = -1
			for i in range(len(self.items)):
				if(self.items[i].pos_x >= cur_x and self.items[i].pos_x <= cur_x + cur_threshold and self.items[i].pos_y > last_pos_y):
					cur_lines[i] = self.items[i].pos_y
					last_pos_y = self.items[i].pos_y  + self.items[i].height * 0.9
			
			cur_lines = sorted(cur_lines.items(), key=lambda kv: kv[1])
			
			# get row_spacing
			row_spacings = []
			for i in range(len(cur_lines)-1):
				cur_item_id, cur_y = cur_lines[i]
				next_item_id, next_y = cur_lines[i+1]
				cur_item = self.items[cur_item_id]
				cur_spacing = next_y - (cur_y + cur_item.height)
				row_spacings.append(cur_spacing)
			
			
			if(len(row_spacings) == 0):
				continue
				
			max_allowed_spacing = statistics.median(row_spacings) * 1.1

			
			for i in range(len(cur_lines)-1):
				cur_item_id, cur_y = cur_lines[i]
				cur_item = self.items[cur_item_id]

				next_item_id, next_y = cur_lines[i+1]
				next_item = self.items[next_item_id]
				if((next_y > cur_y + min(cur_item.height + max_allowed_spacing, 2 * cur_item.height)) or  # too far apart 
				   (cur_item.font_size != next_item.font_size) or  # different font sizes
				   (cur_item.font_file != next_item.font_file)): # different fonts faces
					cur_threshold = 0
					continue
				
				cur_threshold = threshold
				insert_next_id(cur_item_id, next_item_id, self.items)
				#self.items[cur_item_id].next_id = next_item_id
				#self.items[next_item_id].prev_id = cur_item_id
				
		# update all prev_ids 
		for i in range(len(self.items)):
			if(self.items[i].next_id != -1):
				self.items[self.items[i].next_id].prev_id = i
		
	
	def mark_regular_text(self):
		# mark connected text components
		for it in self.items:
			if(it.category != CAT_DEFAULT):
				continue # already taken
			if(it.prev_id != -1):
				continue #has previous item => we look at that
			
			txt = Format_Analyzer.trim_whitespaces(it.txt)
			
			next = it.next_id
			while(next!=-1):
				#print(self.items[next], self.items[next].next_id)
				txt += ' ' + Format_Analyzer.trim_whitespaces(self.items[next].txt)
				next = self.items[next].next_id
				
			if(Format_Analyzer.looks_running_text(txt)):
				it.category = CAT_RUNNING_TEXT
				next = it.next_id
				while(next!=-1):
					self.items[next].category = CAT_RUNNING_TEXT
					next = self.items[next].next_id

	def mark_other_text_components(self):
	
		threshold = int(0.03 * self.page_width + 0.5) # allow max 3% deviation to the left 
		
		for cur_x, cnt in self.left_distrib.items():
				
			cur_lines = {} # for each line in this column, we store its y position
			cur_threshold = 0
			for i in range(len(self.items)):
				if(self.items[i].pos_x >= cur_x and self.items[i].pos_x <= cur_x + cur_threshold):
					cur_threshold = threshold
					cur_lines[i] = self.items[i].pos_y
			
			cur_lines = sorted(cur_lines.items(), key=lambda kv: kv[1])
			
			for i in range(len(cur_lines)):
				cur_item_id, cur_y = cur_lines[i]
				if(self.items[cur_item_id].category  != CAT_DEFAULT):
					continue # already taken
				prev_item_id = -1
				prev_y = -1
				next_item_id = -1
				next_y = -1
				if(i>0):
					prev_item_id, prev_y = cur_lines[i-1]
				if(i<len(cur_lines)-1):
					next_item_id, next_y = cur_lines[i+1]
					
				# between to running texts (paragraphs):
				if(prev_item_id!=-1 and next_item_id!=-1):
					y_threshold = 2*max(self.items[cur_item_id].height, self.items[prev_item_id].height, self.items[next_item_id].height)
					
					if(self.items[prev_item_id].category == CAT_RUNNING_TEXT and self.items[next_item_id].category == CAT_RUNNING_TEXT and
						abs(cur_y-prev_y) < y_threshold and abs(cur_y-next_y) < y_threshold):
						if(self.items[cur_item_id].height > self.items[next_item_id].height):
							self.items[cur_item_id].category = CAT_HEADLINE
						else:
							print_verbose(10, "---->>> found CAT_OTHER_TEXT/1 for item " + str(cur_item_id))
							self.items[cur_item_id].category = CAT_OTHER_TEXT
				
				# single (head-)lines at the beginning
				if((prev_item_id==-1 or self.items[cur_item_id].prev_id == -1)  and next_item_id!=-1):
					y_threshold = 2*max(self.items[cur_item_id].height, self.items[next_item_id].height)
					
					if(self.items[next_item_id].category == CAT_RUNNING_TEXT and
						abs(cur_y-next_y) < y_threshold):
						if(self.items[cur_item_id].height > self.items[next_item_id].height):
							self.items[cur_item_id].category = CAT_HEADLINE
						else:
							print_verbose(10, "---->>> found CAT_OTHER_TEXT/2 for item " + str(cur_item_id))
							self.items[cur_item_id].category = CAT_OTHER_TEXT
				
		
			# multiple rows spanning headlines at the beginning
			for i in range(len(cur_lines)-1):
				cur_item_id, cur_y = cur_lines[i]
				if(self.items[cur_item_id].category  != CAT_DEFAULT):
					continue # already taken
					
				if(self.items[cur_item_id].next_id != -1 or self.items[cur_item_id].prev_id == -1):
					continue # we are only interested at items that mark end of a block
					
				if(not Format_Analyzer.looks_words(self.items[cur_item_id].txt)):
					continue # only text
			
				print_verbose(9, "--> mark_other_text_components \ multi-rows headline: "+str(self.items[cur_item_id]))
				next_item_id, next_y = cur_lines[i+1]	

				if(self.items[next_item_id].category != CAT_RUNNING_TEXT):
					continue # only when followed by normal paragraph
					
				if(self.items[cur_item_id].font_size <= self.items[next_item_id].font_size and
				   not (self.items[cur_item_id].font_size == self.items[next_item_id].font_size and
				        self.items[cur_item_id].is_bold and not self.items[next_item_id].is_bold)):
					continue # header must of greater font size, or: same font size but greater boldness (i.e, headline bold, but following text not)
					
				y_threshold = 2*max(self.items[cur_item_id].height, self.items[next_item_id].height)
				
				print_verbose(9, "----> cur_y, next_y , y_threshold = " + str(cur_y) + ","+str(next_y)+","+str(y_threshold))
				
				
				if(abs(cur_y - next_y) < y_threshold and self.items[cur_item_id].height > self.items[next_item_id].height):
					# count number of affected lines
					iter_item_id = cur_item_id
					num_affected = 1
					while(iter_item_id != -1):
						iter_item_id = self.items[iter_item_id].prev_id		
						num_affected += 1
					if(num_affected <= 3): # more than 3 lines would be too much for a headline
						# match!
						print_verbose(9, "------->> MATCH!")
						iter_item_id = cur_item_id
						while(iter_item_id != -1):
							self.items[iter_item_id].category = CAT_HEADLINE
							iter_item_id = self.items[iter_item_id].prev_id		
			

							
		# Page number and footer
		pgnum_threshold = 0.9 * self.page_height
		pgnum_id = -1
		pgnum_pos_y = 0
		
		for i in range(len(self.items)):
			if(self.items[i].pos_y < pgnum_threshold):
				continue
			if(Format_Analyzer.looks_pagenum(self.items[i].txt)):
				cur_y = self.items[i].pos_y
				if(cur_y > pgnum_pos_y):
					pgnum_pos_y = cur_y
					pgnum_id = i
					
		if(pgnum_id != -1):
			print_verbose(10, "---->>> found CAT_FOOTER/3 for item " + str(pgnum_id))
			self.items[pgnum_id].category = CAT_FOOTER
			for it in self.items:
				if(it.pos_y == pgnum_pos_y):
					print_verbose(10, "---->>> found CAT_FOOTER/4 for item " + str(it.this_id))
					it.category = CAT_FOOTER #footer
		
							
		# Isolated items
		iso_threshold = 0.05 * self.page_height
		
		for it in self.items:
			if(it.category != CAT_DEFAULT):
				continue #already taken
				
			min_dist = 99999999
			
			for jt in self.items:
				if(it==jt or jt.category==CAT_RUNNING_TEXT or jt.category==CAT_HEADLINE or jt.category==CAT_OTHER_TEXT or jt.category==CAT_FOOTER):
					continue # we do not consider these ones (=> text is assumed to be isolated, even if any of these ones are near)
				cur_dist = Rect.raw_rect_distance(it.pos_x, it.pos_y, it.pos_x+it.width, it.pos_y+it.height, jt.pos_x, jt.pos_y, jt.pos_x+jt.width, jt.pos_y+jt.height)
				if(cur_dist<min_dist):
					min_dist=cur_dist
					
			if(min_dist > iso_threshold):
				print_verbose(10, "---->>> found CAT_OTHER_TEXT/5 for item " + str(it.this_id))
				it.category = CAT_OTHER_TEXT
					
	
				
	# =====================================================================================================================
	# Utilities for Table Extraction
	# =====================================================================================================================
	
	def find_vnearest_taken_components(self, initial_item): #search vertically, return nearest top and bottom component (if any)
		FONT_RECT_TOLERANCE = 0.9 #be less restrictive, since the font rect's width is not always accurate
		left_min = initial_item.pos_x
		left_max = initial_item.pos_x + initial_item.width * FONT_RECT_TOLERANCE
		
		top = None
		bottom = None
		
		for it in self.items:
			if(it.has_category_besides(CAT_FOOTER)):
				if(it.pos_x < left_max and it.pos_x + it.width * FONT_RECT_TOLERANCE > left_min):
					if(it.pos_y <= initial_item.pos_y  and (top is None or it.pos_y > top.pos_y)):
						top = it
					if(it.pos_y >= initial_item.pos_y  and (bottom is None or it.pos_y < bottom.pos_y)):
						bottom = it
		
		return top, bottom
		
		
	def sort_out_non_vconnected_items(self, vitems, top_y, bottom_y):
		res = []
		for i in vitems:
			if(self.items[i].pos_y > top_y and self.items[i].pos_y < bottom_y):
				res.append(i)
		
		return res

		
	def sort_out_taken_items(self, any_items):
		res = []
		for i in any_items:
			if(not self.items[i].has_category_besides(CAT_FOOTER) and self.items[i].temp_assignment == 0):
				res.append(i)
		
		return res
		
		
	def sort_out_non_vertical_aligned_items_by_bounding_box(self, initial_item, vitems):
		res = []

		x0 = initial_item.pos_x
		x1 = initial_item.pos_x + initial_item.width
		
		
		
		for i in vitems:
			cur_x0 = self.items[i].pos_x
			cur_x1 = self.items[i].pos_x + self.items[i].width
			
			if(cur_x0 < x1  and cur_x1 > x0 ):
				res.append(i)
			
		return res
				
				
					
					
	def sort_out_items_in_same_row(self, initial_item, vitems):
		orig_pos_x = initial_item.get_aligned_pos_x()
		res = []
		for i in vitems:
			it_delta = abs(self.items[i].get_aligned_pos_x() - orig_pos_x)
			better_item_in_same_row = False
			for j in vitems:
				if(i==j):
					continue
				if(self.items[j].pos_y + self.items[j].height >= self.items[i].pos_y and self.items[j].pos_y <= self.items[i].pos_y + self.items[i].height):
					jt_delta = abs(self.items[j].get_aligned_pos_x() - orig_pos_x)
					if(jt_delta < it_delta):
						better_item_in_same_row = True
						break
			if(not better_item_in_same_row):
				res.append(i)
		
		return res
		
	def sort_out_non_connected_row_items(self, hitems, initial_item):
		# in the same row, we sort out all items, that are not connected with initial_item
		# 2 items are connected, iff between them, there are no taken items
		# initial_item will always be included
		min_x = -1
		max_x = 9999999
		for i in hitems:
			if(self.items[i].has_category_besides(CAT_FOOTER) or self.items[i].temp_assignment != 0):
				cur_x = self.items[i].pos_x
				if(cur_x < initial_item.pos_x):
					min_x = max(min_x, cur_x)
				if(cur_x > initial_item.pos_x):
					max_x = min(max_x, cur_x)
		
		res = []
		for i in hitems:
			if(self.items[i].pos_x > min_x and self.items[i].pos_x < max_x):
				res.append(i)
				
		return res
		
	
	

	
	def discover_table_column(self, initial_item):
		print_verbose(7, 'discover_table_column for item : ' + str(initial_item))

		vitems, dummy = self.find_vertical_aligned_items(initial_item, ALIGN_DEFAULT, DEFAULT_VTHRESHOLD)
		print_verbose(9, '---> 1. V-Items ')
		print_subset(9, self.items, vitems)
		vitems = self.sort_out_taken_items(vitems)
		print_verbose(9, '---> 2. V-Items ')
		print_subset(9, self.items, vitems)
		vitems = self.sort_out_non_vertical_aligned_items_by_bounding_box(initial_item, vitems)
		print_verbose(9, '---> 3. V-Items ')
		print_subset(9, self.items, vitems)
		vitems = self.sort_out_items_in_same_row(initial_item, vitems)
		print_verbose(9, '---> 4. V-Items ')
		print_subset(9, self.items, vitems)
		
		top, bottom = self.find_vnearest_taken_components(initial_item)
		vitems = self.sort_out_non_vconnected_items(vitems, -1 if top is None else top.pos_y, 9999999 if bottom is None else bottom.pos_y)
		
		# make sure, that initial_item is always included
		if(initial_item.this_id not in vitems):
			vitems.append(initial_item.this_id)
		
		print_verbose(7, '---> top: ' + str(top) + ', and bottom:' + str(bottom))
		print_verbose(7, '---> V-Items ')
		print_subset(7, self.items, vitems)
		
		sub_tab = HTMLTable()
		if(len(vitems) > 0):
			sub_tab.init_by_cols(vitems, self.items)
			sub_tab.set_temp_assignment()
			print_verbose(5, 'Sub Table for current column at: ' +str(initial_item) + " = " +str(sub_tab))
			
			
		return sub_tab
		
	
	def discover_table_row(self, initial_item):
		hitems = self.find_horizontal_aligned_items(initial_item)
		hitems = self.sort_out_non_connected_row_items(hitems, initial_item)

		print_verbose(7, "discover row at item: "+ str(initial_item))
		print_subset(7, self.items, hitems)
		
		return hitems
	
	
	def discover_subtables_recursively(self, initial_item, step): #step=0 => discover col; step=1 => discover row. each subtable is a column
		print_verbose(5, "discover subtable rec, at item : " +str(initial_item) + " and step = " +str(step))
		
		if(initial_item.has_category() or (initial_item.temp_assignment != 0 and step == 0)):
			print_verbose(5, "---> recusion end")
			return [] # end recursion
			
		if(step==0): # col
			res = []
			cur_sub_table = self.discover_table_column(initial_item)
			
			if(cur_sub_table.count_actual_items() > 0):
				print_verbose(5, "---> added new subtable")
				res.append(cur_sub_table)
				for i in cur_sub_table.idx:
					if(i!=-1):
						res.extend(self.discover_subtables_recursively(self.items[i], 1))
			return res
		
		elif(step==1): # row
			res = []
			hitems = self.discover_table_row(initial_item)
			print_verbose(5, "---> found hitems = "+str(hitems))
			for i in hitems:
				res.extend(self.discover_subtables_recursively(self.items[i], 0))
			
			return res
		
		return []
	
		
	def discover_table(self, initial_item):
		print_verbose(2, "DISCOVER NEW TABLE AT " + str(initial_item))
		
		done = False
		
		while(not done):
			done = True
		
			initial_item.temp_assignment = 0
			self.clear_all_temp_assignments()
			
			sub_tables = self.discover_subtables_recursively(initial_item, 0)
			if(len(sub_tables) == 0):
				return None
				
			table = sub_tables[0]
			print_verbose(2, "Starting with table: "+str(sub_tables[0]))
			
			for i in range(1,len(sub_tables)):
				print_verbose(5, "Merging table: "+str(sub_tables[i]))
				table = HTMLTable.merge(table, sub_tables[i], self.page_width)
				print_verbose(5, "Next table:" + str(table))
			
			# TODO!!!
			#table.recalc_geometry()
			#table.unfold_patched_numbers()
			table.cleanup_table(self.page_width, self.paragraphs)
			
			if(table.is_good_table()):
				# did we miss any items?
				missing_items = self.find_items_within_rect(table.table_rect, [CAT_HEADLINE, CAT_OTHER_TEXT, CAT_RUNNING_TEXT, CAT_FOOTER])
				if(len(missing_items)>0):
					#yes => reclassify
					print_verbose(2, "Found missing items : " +str(missing_items))
					for i in missing_items:
						self.items[i].category = CAT_DEFAULT
					done = False
				
			
			
		return table
		

	def mark_all_tables(self):
		while(True):
			next = self.find_next_nonclassified_item()
			if(next is None):
				break # we are done
				
			table = self.discover_table(next)
			print_verbose(2, "FOUND TABLE: "+str(table))
			if(config.global_force_special_items_into_table):
				table.force_special_items_into_table()
				
				
			if(table.is_good_table()):
				print_verbose(2, "---> good")
				table.categorize_as_table()
				self.tables.append(table)
			else:
				print_verbose(2, "---> bad")
				table.categorize_as_misc()
				
		# sort out all empty special items
		for t in self.tables:
			tmp_sp_idx = []
			for sp_idx in t.special_idx:
				if(self.items[sp_idx].txt != ''):
					tmp_sp_idx.append(sp_idx)
				else:
					self.items[sp_idx].category = CAT_MISC
			t.special_idx = tmp_sp_idx
			
		# merge non-overlapping rows, if needed
		if(config.global_table_merge_non_overlapping_rows):
			for table in self.tables:
				table.merge_non_overlapping_rows()		
				#pass
	
	def mark_all_footnotes(self):
		
		def apply_cat_unsplit(idx, cat):
			self.items[idx].category = cat
			if(self.items[idx].right_id!=-1):
				apply_cat_unsplit(self.items[idx].right_id, cat)
			
			
		print_verbose(5, "Marking all footnotes . . .")
		for idx in range(len(self.items)):
			if(self.items[idx].left_id != -1):
				continue # skip this
			txt = self.get_txt_unsplit(idx)
			print_verbose(7, "Analyzing==>" + txt+ ", cat=" +str(self.items[idx].category))
			if(self.items[idx].category != CAT_OTHER_TEXT):
				continue # skip this also
			if(Format_Analyzer.looks_footnote(txt)):
				# this is a footnote !
				print_verbose(7, ".....>>> Yes, footnote!") 
				apply_cat_unsplit(idx, CAT_FOOTNOTE)
				self.footnotes_idx.append(idx)
				
			
			
			
			

				
	# =====================================================================================================================
	# Rendering
	# =====================================================================================================================
	
	def render_to_png(self, in_dir, out_dir):
	
		base = Image.open(in_dir+r'/page'+str(self.page_num)+'.png').convert('RGBA').resize((self.page_width, self.page_height))
		context = ImageDraw.Draw(base)
		
		if(not RENDERING_USE_CLUSTER_COLORS):
			table_bg_color = (0,255,255,255) #if not RENDERING_USE_CLUSTER_COLORS else (255, 255, 255, 64)
			
			# table borders
			for t in self.tables:
				context.rectangle([(t.table_rect.x0,t.table_rect.y0),(t.table_rect.x1,t.table_rect.y1)], fill = table_bg_color, outline =(0,0,0,255)) 
				first = True
				for r in t.rows:
					if(first):
						first = False
						context.line([(r.x0, r.y0),(r.x1, r.y0)], fill =(0,0,0,255), width = 0) 
					context.line([(r.x0, r.y1),(r.x1, r.y1)], fill =(0,0,0,255), width = 0) 
				first = True
				for c in t.cols:
					if(first):
						first = False
						context.line([(c.x0, c.y0),(c.x0, c.y1)], fill =(0,0,0,255), width = 0) 
					context.line([(c.x1, c.y0),(c.x1, c.y1)], fill =(0,0,0,255), width = 0) 
					
		
		# text
		if(RENDERING_USE_CLUSTER_COLORS):
			self.clusters_text.generate_rendering_colors_rec()
			
		for it in self.items:
			font_color = (0,0,255,255) #default
			if(it.category in (CAT_RUNNING_TEXT, CAT_HEADLINE, CAT_OTHER_TEXT, CAT_FOOTER)):
				font_color = (216, 216, 216, 255)
				
			#if(it.category == CAT_HEADLINE):
			#	font_color = (0, 128, 32, 255)
				
			#if(it.category == CAT_OTHER_TEXT):
			#	font_color = (0, 255, 0, 255)
			
			if(it.category == CAT_TABLE_DATA):
				font_color = (0, 0, 0, 255)
			
			if(it.category == CAT_TABLE_HEADLINE):
				font_color = (255, 0, 0, 255)
			
			if(it.category == CAT_TABLE_SPECIAL):
				font_color = (255, 0, 128, 255)
			
			if(it.category == CAT_FOOTNOTE):
				font_color = (127, 0, 255, 255)
			
			"""
			# Color by alignment:
			if(it.alignment == ALIGN_LEFT):
				font_color = (255, 0, 0, 255)
			else:
				font_color = (0, 0, 255, 255)
			"""
			
			"""
			# Color by split:
			if(it.has_been_split):
				font_color = hsv_to_rgba((it.this_id % 6)/6.0, 1, 1)
			else:
				font_color = (128, 128, 128, 255)			
			"""
			
			if(RENDERING_USE_CLUSTER_COLORS):
				font_color = it.rendering_color
			
			span_font = ImageFont.truetype(it.font_file if config.global_rendering_font_override == "" else config.global_rendering_font_override, it.font_size)
			context.text((it.pos_x,it.pos_y), it.txt, font=span_font, fill=font_color)
			
			#for w in it.words:
			#	context.text(( w.rect.x0, w.rect.y0), w.txt, font=span_font, fill=font_color)
			
		

		# conntected lines
		for it in self.items:
			if(it.next_id != -1 and it.category == CAT_RUNNING_TEXT):
				line_shape = [(it.pos_x + 5, int(it.pos_y + it.height / 2)), (self.items[it.next_id].pos_x + 5, self.items[it.next_id].pos_y + int(self.items[it.next_id].height / 2))]
				context.line(line_shape, fill =(80,80,80,255), width = 0) 

		
		base.save(out_dir+r'/output'+"{:05d}".format(self.page_num) +'.png')
		


	# =====================================================================================================================
	# Clustering procedures
	# =====================================================================================================================		

	def generate_clusters(self):
		self.clusters = HTMLCluster.generate_clusters(self.items, CLUSTER_DISTANCE_MODE_EUCLIDIAN)
		self.clusters_text = HTMLCluster.generate_clusters(self.items, CLUSTER_DISTANCE_MODE_RAW_TEXT)
		
				
	# =====================================================================================================================
	# Other procedures
	# =====================================================================================================================		
		
	def remove_certain_items(self, txt, threshold): #they would confuse tables and are not needed
		count = 0
		for it in self.items:
			for w in it.words:
				if(w.txt==txt):
					count += 1
					
		#print('-->count: '+str(count))
					
		if(count >= threshold):
			new_items = []
			cur_id = 0
			for it in self.items:
				new_words = []
				for w in it.words:
					if(w.txt!=txt):
						w.item_id = cur_id
						new_words.append(w)
				if(len(new_words)==0):
					continue # skip this item
				
				it.this_id = cur_id
				it.words = new_words
				it.recalc_geometry()
				it.rejoin_words()	
				new_items.append(it)
				cur_id += 1
				
			self.items = new_items
	
	def remove_flyspeck(self):
		threshold = DEFAULT_FLYSPECK_HEIGHT * self.page_height
		new_items = []
		cur_id = 0
		for it in self.items:
			if(it.height>threshold):
				it.this_id = cur_id
				new_items.append(it)
				cur_id += 1
			else:
				print_verbose(6,"Removing flyspeck item : " + str(it))
			
				
		self.items = new_items
		
	
	
	def remove_overlapping_items(self):
	
		keep = [True] * len(self.items)
		
		for i in range(len(self.items)-1):
			if(keep[i]):
				for j in range(i+1, len(self.items)):
					if(Rect.calc_intersection_area(self.items[i].get_rect(), self.items[j].get_rect()) > 0.):
						#overlapping items => remove it
						keep[j] = False
						print_verbose(5, "Removing item : " + str(self.items[j]) + ", because overlap with : " + str(self.items[i]))
		
		new_items = []
		cur_id = 0
		for i in range(len(self.items)):
			if(keep[i]):
				self.items[i].this_id = cur_id
				new_items.append(self.items[i])
				cur_id += 1
		
		self.items = new_items
	
	def save_all_tables_to_csv(self, outdir):
		for i in range(len(self.tables)):
			self.tables[i].save_to_csv(remove_trailing_slash(outdir) + r'/tab_' + str(self.page_num) + r'_' + str(i+1) + r'.csv')
			
	def save_all_footnotes_to_txt(self, outdir):
		if(len(self.footnotes_idx) == 0):
			return # dont save if empty
		res = ""
		for idx in self.footnotes_idx:
			res += self.get_txt_unsplit(idx) + "\n"
		
		save_txt_to_file(res, remove_trailing_slash(outdir) + r'/footnotes_' + str(self.page_num) + r'.txt')
	
	
	def preprocess_data(self):
		self.remove_flyspeck()
		self.remove_certain_items('.', 50)
		#self.remove_certain_items('', 1)
		self.remove_overlapping_items()
		self.detect_split_items()
		self.find_left_distributions()
		self.guess_all_alignments()
		self.identify_connected_txt_lines()
		self.mark_regular_text()
		self.mark_other_text_components()
		self.find_paragraphs()
		self.mark_all_tables()
		self.mark_all_footnotes()
		self.generate_clusters()
		

		#tmp = self.discover_table_column(self.items[self.find_idx_of_item_by_txt(r'Group statement of changes in equity a')])
		#print(tmp)
		
	"""
	# TODO: Remove this procedure
	def test(self):
		tmp = self.discover_table_column(self.items[self.find_idx_of_item_by_txt(r'$ per barrel')])
		tmp1 = self.discover_table_column(self.items[self.find_idx_of_item_by_txt(r'Refinery throughputs ac')])
		xx = HTMLTable.merge(tmp, tmp1, self.page_width)
		xx.cleanup_table()
		print(tmp)
		print(tmp1)
		print(xx)
	"""	
		
		
	def __repr__(self):
		res = "====>>> HTMLPage : No. = " + str(self.page_num)  + ", Width = " + str(self.page_width) + ", Height = " + str(self.page_height) 
		for i in range(len(self.items)):
			res = res + "\n" +str(i)+". "+ str(self.items[i]) 
			
		res += "\n=====>>> LIST OF TABLES:\n"
		for t in self.tables:
			res = res + str(t)
		return res
		
	def repr_tables_only(self):
		res = "====>>> HTMLPage : No. = " + str(self.page_num)
			
		res += "\n=====>>> LIST OF TABLES:\n"
		for t in self.tables:
			res = res + t.get_printed_repr()
		return res
	
	
	def to_json(self):
		for t in self.tables:
			t.items = None
		
		if(self.clusters is not None):
			self.clusters.cleanup_for_export()
		if(self.clusters_text is not None):
			self.clusters_text.cleanup_for_export()
		
		#data = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
		jsonpickle.set_preferred_backend('json')
		jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
		data = jsonpickle.encode(self)

		for t in self.tables:
			t.items = self.items

		if(self.clusters is not None):
			self.clusters.regenerate_not_exported(self.items)
		if(self.clusters_text is not None):
			self.clusters_text.regenerate_not_exported(self.items)
			
			
		return data
		
	def save_to_file(self, json_file):
		data = self.to_json()
		f = open(json_file, "w")
		f.write(data)
		f.close()
		
	@staticmethod
	def load_from_json(data):
		obj = jsonpickle.decode(data)

		for t in obj.tables:
			t.items = obj.items
			
		# regenerate clustes, if they are not available
		if(obj.clusters is None or obj.clusters_text is None):
			obj.generate_clusters()
		else:
			#just fill up clusters with missing values
			obj.clusters.regenerate_not_exported(obj.items)
			obj.clusters_text.regenerate_not_exported(obj.items)
			
			
			
		return obj
		
	@staticmethod
	def load_from_file(json_file):
		f = open(json_file, "r")
		data = f.read()
		f.close()
		return HTMLPage.load_from_json(data)
		
	
	
	@staticmethod
	def fix_strange_encryption(htmlfile):
		#print(htmlfile)
		bak_file = htmlfile + ".bak"
		
		new_bytes = []
		old_bytes = []
		detected_strange_char = 0
		
		with open(htmlfile, "rb") as f:
			b0 = f.read(1)
			while b0:
				b_out = 0
				c0 = int.from_bytes(b0, byteorder='big')
				if(c0==195):
					#strange character found
					detected_strange_char += 1
					
					b1 = f.read(1)
					c1 = int.from_bytes(b1, byteorder='big')
					chr = 0

					if(c1 >= 95 and c1 <= 191):
						chr = 191 - c1 + 33
					else:
						print("BAD CHARACTER FOUND: 195+-->" + str(c1))
						exit()
					
					b_out = chr.to_bytes(1, 'big')
					
					
				elif(c0==194):
					#strange character found
					detected_strange_char += 1
					
					b1 = f.read(1)
					c1 = int.from_bytes(b1, byteorder='big')
					chr = 0

					if(c1 >= 160 and c1 <= 255):
						chr = 255 - c1 + 33
					else:
						print("BAD CHARACTER FOUND: 194+-->" + str(c1))
						exit()						
						
					b_out = chr.to_bytes(1, 'big')
				else:
					b_out = b0
				
				nb = int.from_bytes(b_out, byteorder='big')
				if(nb == c0 or (nb != 60 and nb!= 62)): #ignore < and >
					new_bytes.append(nb)
				else:
					new_bytes.append(32) #space
					
				old_bytes.append(c0)
				
				#print(b_out)
				b0 = f.read(1)
				
		if(detected_strange_char > 10):
			if(len(old_bytes) != len(new_bytes)):
				#whoops, something went really wrong
				print("old_bytes doesnt match new_bytes!")
				exit()
		
			# replace stupid "s" case and check if we really have strange case
			hit_body = False
			is_txt = True
			good_old_bytes = 0
			for i in range(len(new_bytes)):
				if(i < len(new_bytes) - 6):
					#<body> = 60,98,111,100,121,62
					if(new_bytes[i]==60 and new_bytes[i+1]==98 and new_bytes[i+2]==111 and new_bytes[i+3]==100 and new_bytes[i+4]==121 and new_bytes[i+5]==62):
						hit_body = True
				if(i>0 and new_bytes[i-1] == 62):
					is_txt = True
				if(new_bytes[i] == 60):
					is_txt = False
				if(hit_body and is_txt and new_bytes[i]==45):
					new_bytes[i] = 115 #s
				if(hit_body and is_txt and old_bytes[i]==new_bytes[i]):
					good_old_bytes +=1
			
			if(detected_strange_char < good_old_bytes * 2):
				return # too few strange characters
			
			shutil.copy(htmlfile, bak_file)
			with open(htmlfile, "wb") as f:
				f.write(bytes(new_bytes))
				
				
		
	
	@staticmethod
	def parse_html_file(fonts_dir, htmlfile):
		pattern_pgnum = re.compile('.*page([0-9]+)\\.html')
		pattern_background = re.compile('<img id="background" style="position:absolute; (left|right):0px; (top|bottom):0px;" width="([0-9]+)" height="([0-9]+)" src="page([0-9]+)\.png">')
		pattern_div  = re.compile('<div class="txt" style="position:absolute; (left|right):([0-9]+)px; top:([0-9]+)px;">(<span id="f[0-9]+" style="font-size:[0-9]+px;vertical-align:.*;color:rgba\([0-9]+,[0-9]+,[0-9]+,[0-9]+\);">.*</span>)</div>')
		pattern_span = re.compile('<span id="f([0-9]+)" style="font-size:([0-9]+)px;vertical-align:.*;color:rgba\(([0-9]+),([0-9]+),([0-9]+),([0-9]+)\);">(.*)')
		# <div class="txt" style="position:absolute; left:42px; top:169px;"><span id="f4" style="font-size:8px;vertical-align:baseline;color:rgba(0,0,0,1);">direct GHGs)</span></div>
		
		pattern_bbox = re.compile('\(([0-9]+\.[0-9]+),([0-9]+\.[0-9]+)\)-\(([0-9]+\.[0-9]+),([0-9]+\.[0-9]+)\)-->(.*)')
		#<!--BBox:(239.92,769.53)-(250.03,776.52)-->
		
		pattern_font  = re.compile('#f([0-9]+) { font-family:ff([0-9]+)[^0-9].*; }')
		pattern_bold  = re.compile('#f([0-9]+) { font-family:.*; font-weight:bold; font-style:.*; }')
		##f1 { font-family:ff0,sans-serif; font-weight:bold; font-style:normal; }
		
		pattern_font_url = re.compile(r'@font-face { font-family: ff([0-9]+); src: url\("([0-9]+\.ttf|([0-9]+)\.otf)"\); }')
		#@font-face { font-family: ff24; src: url("24.ttf"); }
		
		
		print_verbose(2, "PARSING HTML-FILE " + htmlfile)
		
		page_num = int(pattern_pgnum.match(htmlfile).groups()[0])
		print_verbose(4, "---> Page: " + str(page_num))
		bold_styles = []
		font_dict = {}
		font_url_dict = {}
		
		res = HTMLPage()
		
		cur_item_id = 0
		
		with open(htmlfile, errors='ignore', encoding=config.global_html_encoding) as f:
			html_file = f.readlines()
		
		for i in range(0, len(html_file)):
			h = html_file[i].strip()
			print_verbose(7, '---->' + h)
			if(pattern_background.match(h)):
				bg = pattern_background.match(h).groups()
				res.page_num = int(bg[2+2])
				res.page_width = int(bg[0+2])
				res.page_height = int(bg[1+2])
			if(pattern_font.match(h)):
				f = pattern_font.match(h).groups()
				font_dict[int(f[0])] = int(f[1])
				print_verbose(7, 'Font-> f='+str(f))
			if(pattern_font_url.match(h)):
				fu = pattern_font_url.match(h).groups()
				font_url_dict[int(fu[0])] = fu[1]
			if(pattern_bold.match(h)):
				b = pattern_bold.match(h).groups()
				bold_styles.append(b[0])
				print_verbose(7, 'Bold->' + str(b))
			if(pattern_div.match(h)):
				g = pattern_div.match(h).groups()
				print_verbose(7, '-------->' + str(g))
				spans = g[2+1].split('</span>')
				print_verbose(7, '-------->' + str(spans))
				item = None
				item = HTMLItem()
				item.line_num = i
				item.tot_line_num = page_num * 10000 + i
				item.this_id = cur_item_id
				#item.pos_x = int(g[0+1])
				#item.pos_y = int(g[1+1])
				item.txt = ''
				item.is_bold = False
				#item.width = 0
				#item.height = 0
				item.font_size = 0
				item.brightness = 255
				item.page_num = page_num
				space_width = 0
				for s in spans:
					if(pattern_span.match(s)):
						gs = pattern_span.match(s).groups()
						print_verbose(7, '---------->' + str(gs))
						if(gs[0] in bold_styles):
							item.is_bold = True
						
						#print("font_url_dict="+str(font_url_dict))
						#print("font_dict="+str(font_dict))
						
						span_font = None
						if(int(gs[0]) in font_dict and font_dict[int(gs[0])] in font_url_dict):
							span_font = ImageFont.truetype(fonts_dir + '/' + font_url_dict[font_dict[int(gs[0])]] , int(gs[1]))
							item.font_file = fonts_dir + '/' + font_url_dict[font_dict[int(gs[0])]]
						else:
							span_font = ImageFont.truetype(config.global_approx_font_name , int(gs[1]))
							item.font_file = config.global_approx_font_name
						
						try:
							space_width = max(space_width, get_text_width(' ', span_font), get_text_width('x', span_font))
						except:
							span_font = ImageFont.truetype(config.global_approx_font_name , int(gs[1]))
							item.font_file = config.global_approx_font_name							
							space_width = max(space_width, get_text_width(' ', span_font), get_text_width('x', span_font))
						
						#text_width = get_text_width(gs[6], int(gs[1]), span_font)
						#if(text_width == 0):
						#	print_verbose(5, "Warning! Found font with 0 for "+ str(fonts_dir + '\\' + font_url_dict[font_dict[int(gs[0])]]) + ", h="+str(int(gs[1]))+", txt='"+gs[6])
						#	text_width = get_text_width("x"*max(1,len(gs[6])), int(gs[1]), span_font) #approximate
						#item.width += text_width
						#item.height = max(item.height, int(gs[1]))
						item.font_size = max(item.font_size, int(gs[1]))
						#item.txt += (' ' if item.txt != '' else '') + gs[6] if gs[6] != '' else '-'
						item.brightness = min(item.brightness, (int(gs[2])+int(gs[2])+int(gs[2]))/3)
						span_text = gs[6]
						bboxes = span_text.split('<!--BBox:')
						for b in bboxes:
							if(pattern_bbox.match(b)):
								bs = pattern_bbox.match(b).groups()
								word = HTMLWord()
								word.txt = Format_Analyzer.trim_whitespaces(html.unescape(bs[4]))
								word.rect.x0 = float(bs[0])
								word.rect.y0 = float(bs[1])
								word.rect.x1 = float(bs[2])
								word.rect.y1 = float(bs[3])
								word.item_id = cur_item_id
								if(word.rect.x0 < word.rect.x1 and word.rect.y0 < word.rect.y1): # otherwise, bad word!
									item.words.append(word)
				
				item.space_width = max(space_width, get_text_width(' ',ImageFont.truetype(config.global_approx_font_name, item.font_size)))
				#print(item.space_width)
				#item.space_width = get_text_width(' ',ImageFont.truetype(config.global_approx_font_name, item.font_size))
				item.fix_overlapping_words()
				item.recalc_geometry()
				item.rejoin_words()
				#if(item.width == 0):
				#	raise ValueError("Item "+str(item) + " with font " +str(fonts_dir + '\\' + font_url_dict[font_dict[int(gs[0])]]) + ", h="+str(int(gs[1])) +" has width == 0")
				print_verbose(7, item)
				res.items.append(item)
				cur_item_id += 1

		
		res.preprocess_data()
				
		return res
	
	
