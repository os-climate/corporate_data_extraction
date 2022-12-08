# ============================================================================================================================
# PDF_Analyzer
# File   : HTMLWord.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 HTMLItem consistens of * HTMLWords
# ============================================================================================================================

from globals import *
from Rect import *


class HTMLWord:
	txt		= None
	rect	= None
	item_id	= None # to which HTMLItem id does this word belong?
	
	
	def __init__(self):
		self.txt = ''
		self.rect = Rect(99999,99999,-1,-1)
		self.item_id = -1

