# ============================================================================================================================
# PDF_Analyzer
# File   : HTMLItem.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 HTMLItem consistens of * HTMLWords
# Note   : 1 HTMLPage consistens of * HTMLItems
# ============================================================================================================================

from globals import *
from HTMLWord import *
from Format_Analyzer import *


class HTMLItem:
	line_num 		= None
	tot_line_num	= None
	pos_x 			= None # in pixels
	pos_y 			= None # in pixels
	width			= None # in pixels
	height			= None # in pixels
	initial_height	= None # in pixels
	font_size		= None
	txt 			= None
	is_bold 		= None
	brightness		= None
	alignment		= None
	font_file		= None
	
	this_id			= None 
	next_id			= None # next line, -1 if None
	prev_id			= None # prev line, -1 if None
	left_id			= None # item to the left, -1 if None
	right_id		= None # item to the right, -1 if None
	
	category		= None
	temp_assignment	= None # an integer, that is normally set to 0. It has greater values while table extraction is in progress
	
	merged_list		= None #indexes of items, that this item had been merged with
	words			= None #list of all words (each a HTMLWord)
	space_width 	= None
	has_been_split	= None
	
	rendering_color	= None # only used for PNG rendering. not related with KPI extraction
	
	page_num		= None
	
	
	def __init__(self):
		self.line_num 	= 0
		self.tot_line_num = 0
		self.pos_x 		= 0
		self.pos_y 		= 0
		self.width 		= 0
		self.height 	= 0
		self.initial_height = None
		self.font_size 	= 0
		self.txt 		= ""
		self.is_bold 	= False
		self.brightness = 255
		self.alignment	= ALIGN_LEFT
		self.font_file	= ""
		self.this_id 	= -1
		self.next_id 	= -1
		self.prev_id	= -1
		self.category 	= CAT_DEFAULT
		self.temp_assignment = 0
		self.merged_list = []
		self.words = []
		self.space_width = 0
		self.has_been_split = False
		self.left_id 	= -1
		self.right_id	= -1
		self.rendering_color = (0,0,0,255) #black by default
		self.page_num = -1

	
	def is_connected(self):
		return next_id != -1 or prev_id != -1
		
	def get_depth(self):
		size = self.font_size
		if(len(self.words)>0):
			size = 0
			for w in self.words:
				size = max(size, w.rect.y1 - w.rect.y0)
			if(size < self.font_size * 0.8):
				size = self.font_size *0.8
			if(size > self.font_size * 1.2):
				size = self.font_size * 1.2
		return 10000 - int(size * 10 + (5 if self.is_bold else 0) + (3 * (255 - self.brightness)) / 255)
		
	def get_aligned_pos_x(self):
		if(self.alignment == ALIGN_LEFT):
			return self.pos_x
		if(self.alignment == ALIGN_RIGHT):
			return self.pos_x + self.width
		if(self.alignment == ALIGN_CENTER): # New-27.06.2022
			return self.pos_x + self.width * 0.5
		# not yet implemented:
		return None
		
	def is_text_component(self):
		return self.category == CAT_HEADLINE or self.category == CAT_OTHER_TEXT or self.category == CAT_RUNNING_TEXT or self.category == CAT_FOOTER

	def has_category(self):
		return self.category != CAT_DEFAULT
		
	def has_category_besides(self, category_to_neglect):
		return self.category != CAT_DEFAULT and self.category != category_to_neglect
		
	def get_rect(self):
		return Rect(self.pos_x,self.pos_y,self.pos_x+self.width,self.pos_y+self.height)
		
	@staticmethod
	def find_item_by_id(items, id):
		for it in items:
			if(it.this_id == id):
				return it
		return None # not found. should never happen
		
	def reconnect(self, next_it, all_items):
		if(self.next_id != -1):
			old_next_it = HTMLItem.find_item_by_id(all_items, self.next_id)
			old_next_it.prev_id = -1

		if(next_it.prev_id != -1):
			new_next_olds_prev_it = HTMLItem.find_item_by_id(all_items, next_it.prev_id)
			new_next_olds_prev_it.next_id = -1
		
		self.next_id = next_it.this_id
		next_it.prev_id = self.this_id
		
	def is_mergable(self, it):
		if(self.next_id == -1 and it.next_id == -1):
			return False
		if(self.prev_id == -1 and it.prev_id == -1):
			return False
		return (self.next_id == it.this_id or self.prev_id == it.this_id) \
			and self.pos_x == it.pos_x \
			and self.font_file == it.font_file \
			and self.height == it.height \
			and not Format_Analyzer.looks_numeric(self.txt) \
			and not Format_Analyzer.looks_numeric(it.txt)
			
	def is_weakly_mergable_after_reconnect(self, it):
		return self.font_file == it.font_file \
			and self.font_size == it.font_size \
			and abs(self.get_initial_height() - it.get_initial_height()) < 0.1
			
	def get_font_characteristics(self):
		return self.font_file + '???' + str(self.font_size) + '???' + str(self.brightness) + '???' +str(self.is_bold)
		
	def get_initial_height(self):
		if(self.initial_height is not None):
			return self.initial_height
		return self.height
		
		
	def recalc_width(self):
		span_font = ImageFont.truetype(self.font_file, self.font_size)
		size = span_font.getsize(self.txt)
		self.width = size[0]
		if(self.width == 0):
			#aproximate
			size = span_font.getsize('x' * len(self.txt))
			self.width = size[0]
			
		
	def merge(self, it):
		# precondition : both items must be mergable
		if(self.next_id == it.this_id):
			self.txt += '\n' + it.txt
			self.initial_height = self.get_initial_height()
			self.height = it.pos_y + it.height - self.pos_y
			self.width = max(self.width, it.width)
			self.words = self.words + it.words
			it.words = []
			it.txt = ''
		elif(self.prev_id == it.this_id):
			it.txt += '\n' + self.txt
			it.initial_height = it.get_initial_height()
			it.height = self.pos_y + self.height - it.pos_y
			it.width = max(self.width, it.width)
			it.words = self.words + it.words
			self.txt = ''
			self.words = []
		else:
			raise ValueError('Items '+str(self)+' and '+str(it) + ' cannot be merged.')
		
		old_merged_list = self.merged_list.copy()
		self.merged_list.append(it.this_id)
		self.merged_list.extend(it.merged_list)
		it.merged_list.append(self.this_id)
		it.merged_list.extend(old_merged_list)
		
		
	def fix_overlapping_words(self):
		# assertion: all words are ordered by x asceding
		for i in range(len(self.words)-1):
			self.words[i].rect.x1 = min(self.words[i].rect.x1, self.words[i+1].rect.x0 - 0.00001)
			
		
	def recalc_geometry(self):
		self.pos_x = 9999999
		self.pos_y = 9999999
		x1 = -1
		y1 = -1
		for w in self.words:
			self.pos_x = min(self.pos_x, w.rect.x0)
			self.pos_y = min(self.pos_y, w.rect.y0)
			x1 = max(x1, w.rect.x1)
			y1 = max(y1, w.rect.y1)
		self.width = x1 - self.pos_x
		self.height = y1 - self.pos_y
		
	def rejoin_words(self):
		self.txt = ''
		for w in self.words:
			if(self.txt != ''):
				self.txt += ' '
			self.txt += w.txt
		
		

	def split(self, at_word, next_item_id):
		# example "abc 123 def" -> split(1, 99) -> 
		# result "abc", and new item with item_id=99 "123 def"
		new_item = HTMLItem()
		new_item.line_num 		= self.line_num 		
		new_item.tot_line_num	= self.tot_line_num	
		#new_item.pos_x 			= self.pos_x
		#new_item.pos_y 			= self.pos_y 			
		#new_item.width			= self.width			
		#new_item.height			= self.height			
		new_item.font_size		= self.font_size		
		new_item.words			= self.words[at_word:]
		#new_item.txt 			= self.txt
		new_item.is_bold 		= self.is_bold 		
		new_item.brightness		= self.brightness		
		new_item.alignment		= self.alignment		
		new_item.font_file		= self.font_file		
		new_item.this_id		= next_item_id
		new_item.next_id		= -1	
		new_item.prev_id		= -1	
		new_item.category		= self.category		
		new_item.temp_assignment= self.temp_assignment
		new_item.merged_list	= self.merged_list	
		new_item.space_width 	= self.space_width
		new_item.has_been_split = True
		
		self.has_been_split 	= True
		
		new_item.left_id 		= self.this_id
		new_item.right_id		= self.right_id
		new_item.page_num		= self.page_num
		self.right_id			= new_item.this_id
		
		for k in range(at_word, len(self.words)):
			self.words[k].item_id = next_item_id
		
		self.words = self.words[0:at_word]
		self.recalc_geometry()
		self.rejoin_words()
		
		new_item.recalc_geometry()
		new_item.rejoin_words()
		
		return new_item
	
#	def unsplit(self, right):
#		self.words = self.words + right.words
#		self.right_id = right.right_id
#		self.recalc_geometry()
#		self.rejoin_words()		
#		# afterwards, right needs to be discarded
	

	@staticmethod
	def concat_txt(item_list, sep=' '):
		res = ''
		for it in item_list:
			if(res != ''):
				res += sep
			res += it.txt
		return res
		 

	def __repr__(self):
		return "<HTMLItem: line_num="+str(self.line_num)+", pos_x="+str(self.pos_x)+", pos_y="+str(self.pos_y)+", is_bold="+str(self.is_bold)+", width="+str(self.width) \
			+", height="+str(self.height)+", init_height="+str(self.get_initial_height()) \
			+ ", align=" + ("L" if self.alignment==ALIGN_LEFT else "R" if self.alignment==ALIGN_RIGHT else "C") +", brightness="+str(self.brightness) \
			+ (", cat="+str(self.category)+", tmp_ass="+str(self.temp_assignment) if config.global_verbosity>=8 else "") \
			+", depth="+str(self.get_depth())+",font_size="+str(self.font_size)+ ", txt='"+self.txt+"', id="+str(self.this_id)+", pid="+str(self.prev_id)+", nid="+str(self.next_id)+">"

