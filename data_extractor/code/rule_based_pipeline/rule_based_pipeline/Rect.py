# ============================================================================================================================
# PDF_Analyzer
# File   : Rect.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
# ============================================================================================================================

from globals import *


class Rect:
	x0 = None
	x1 = None
	y0 = None
	y1 = None


	def __init__(self):
		self.x0 = 0
		self.x1 = 0
		self.y0 = 0
		self.y1 = 0

	def __init__(self, x0_, y0_, x1_, y1_):
		self.x0 = x0_
		self.x1 = x1_
		self.y0 = y0_
		self.y1 = y1_

		
	def get_width(self):
		return self.x1 - self.x0
	
	def get_height(self):
		return self.y1 - self.y0
		
	def get_area(self):
		return self.get_width() * self.get_height()
		
	def grow(self, rect):
		self.x0 = min(self.x0, rect.x0)
		self.y0 = min(self.y0, rect.y0)
		self.x1 = max(self.x1, rect.x1)
		self.y1 = max(self.y1, rect.y1)
		
	def get_center(self):
		return (self.x1+self.x0) * 0.5, (self.y1+self.y0) * 0.5
		
	@staticmethod
	def raw_rect_distance(x1, y1, x1b, y1b, x2, y2, x2b, y2b):
		#see: https://stackoverflow.com/questions/4978323/how-to-calculate-distance-between-two-rectangles-context-a-game-in-lua
		left = x2b < x1
		right = x1b < x2
		bottom = y2b < y1
		top = y1b < y2
		if top and left:
			return dist(x1, y1b, x2b, y2)
		elif left and bottom:
			return dist(x1, y1, x2b, y2b)
		elif bottom and right:
			return dist(x1b, y1, x2, y2b)
		elif right and top:
			return dist(x1b, y1b, x2, y2)
		elif left:
			return x1 - x2b
		elif right:
			return x2 - x1b
		elif bottom:
			return y1 - y2b
		elif top:
			return y2 - y1b
		else:             # rectangles intersect
			return 0.		
			
		
	@staticmethod
	def calc_intersection_area(r1, r2):
		return max(0, min(r1.x1, r2.x1) - max(r1.x0, r2.x0)) * max(0, min(r1.y1, r2.y1) - max(r1.y0, r2.y0))
		
	@staticmethod
	def distance(r1, r2):
		return Rect.raw_rect_distance(r1.x0, r1.y0, r1.x1, r1.y1, r2.x0, r2.y0, r2.x1, r2.y1)
		
	def get_coordinates(self):
		return (self.x0,self.y0)
		
	def __repr__(self):
		return "<Rect: (" +str(self.x0)+","+str(self.y0)+") - ("+str(self.x1)+","+str(self.y1)+") >"


