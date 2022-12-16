# ============================================================================================================================
# PDF_Analyzer
# File   : HTMLCluster.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 HTMLPage consistens of 1 HTMLCluster (root-node)
# Note   : 1 HTMLCluster contains * HTMLClusters (internal nodes), or consists of 1 HTMLItem (leaf node)
# ============================================================================================================================

from globals import *
from HTMLItem import *

import scipy.cluster.hierarchy as hcl
from scipy.spatial.distance import squareform
import numpy

CLUSTER_DISTANCE_MODE_EUCLIDIAN = 0
CLUSTER_DISTANCE_MODE_RAW_TEXT 	= 1


class HTMLCluster:

	idx			= None
	#rect		= None
	children	= None
	items		= None #dont export
	flat_text	= None #dont export

	
	def __init__(self):
		self.idx = -1
		self.children = []
		self.items = []
		#self.rect = Rect(99999,99999,-1,-1)
		self.flat_text = "" 


		
	def is_internal_node(self):
		return len(self.children) > 0
		
	def is_leaf(self):
		return self.idx != -1
	
	def set_idx(self, idx):
		if(self.is_internal_node()):
			raise ValueError('Node '+str(self) + ' is already an internal node')
		self.idx = idx # now it's a child node
		
	def add_child(self, child):
		if(self.is_leaf()):
			raise ValueError('Node '+str(self) + ' is already a leaf node')
		self.children.append(child)
		
	def calc_flat_text(self):
		if(self.is_leaf()):
			self.flat_text = str(self.items[self.idx].txt)
			return
		first = True
		res = ""
		for c in self.children:
			if(not first):
				res += ", "
			c.calc_flat_text()
			res += c.flat_text
			first = False
		self.flat_text = res
		
	def get_idx_list(self):
		if(self.is_leaf()):
			return [self.idx]
			
		res =[]
		for c in self.children:
			res.extend(c.get_idx_list())
		return res
			

	def set_items_rec(self, items):
		self.items = items
		for c in self.children:
			c.set_items_rec(items)
			
	def count_items(self):
		if(self.is_leaf()):
			return 1
		res = 0
		for c in self.children:
			res += c.count_items()
		return res
	
	def generate_rendering_colors_rec(self, h0=0.0, h1=0.75): # h = hue in [0,1]
		if(self.is_leaf()):
			self.items[self.idx].rendering_color = hsv_to_rgba((h0+h1)*0.5, 1, 1)
		else:
			num_items_per_child = []
			num_items_tot = 0
			for c in self.children:
				cur_num = c.count_items()
				num_items_per_child.append(cur_num)
				num_items_tot += cur_num
			num_items_acc  = 0
			for i in range(len(self.children)):
				self.children[i].generate_rendering_colors_rec(h0 + (h1-h0) * (num_items_acc/num_items_tot), h0 + (h1-h0) * ((num_items_acc + num_items_per_child[i]) /num_items_tot))
				num_items_acc += num_items_per_child[i]
		
		
		
	def regenerate_not_exported(self, items):
		self.set_items_rec(items)
		self.calc_flat_text()

		
	def cleanup_for_export(self):
		self.items = None
		self.flat_text = None
		for c in self.children:
			c.cleanup_for_export()
			
		
	def __repr__(self):
		if(self.is_leaf()):
			return str(self.items[self.idx])
		res = "<"
		first = True
		for c in self.children:
			if(not first):
				res += ", "
			res += str(c)
			first = False
		res += ">"
		return res
		
		
	@staticmethod
	def item_dist(it1, it2, mode):
		if(mode == CLUSTER_DISTANCE_MODE_EUCLIDIAN):
			it1_x, it1_y = it1.get_rect().get_center()
			it2_x, it2_y = it2.get_rect().get_center()
			return dist(it1_x, it1_y, it2_x, it2_y)
		elif(mode == CLUSTER_DISTANCE_MODE_RAW_TEXT):
			return dist(0, it1.pos_y, 0, it2.pos_y)
			#return dist(it1.pos_x * 100, it1.pos_y, it2.pos_x * 100, it2.pos_y) #TODO: Add this a a new distance mode ! (20.09.2022)
			
			
			
			
		raise ValueError('Invalid distance mode')
		
		
	@staticmethod
	def generate_clusters(items, mode):
		print_verbose(3, "Regenerating clusters")
		
		if(len(items) < 2):
			return None
		
		# generate a leaf for each items
		nodes = []
		
			
		for it in items:
			cur = HTMLCluster()
			cur.items = items
			cur.idx = it.this_id
			nodes.append(cur)
			
			
		print_verbose(3, 'Leaves: ' + str(nodes))
		
		# generate distance matrix
		l = len(items)
		dmatrix = numpy.zeros((l, l))
		for i in range(l):
			for j in range(i+1,l):
				d = HTMLCluster.item_dist(items[i], items[j], mode)
				dmatrix[i, j] = d
				dmatrix[j, i] = d
		
		
		print_verbose(5, dmatrix)
		
		# compute clusters
		
		sq = squareform(dmatrix)
		
		output_linkage = hcl.linkage(sq, method='average')
		
		# build up tree
		
		num_rows = numpy.size(output_linkage, 0)
		
		print_verbose(5, output_linkage)
		
		for i in range(num_rows):
			cur_cluster = HTMLCluster()
			cur_cluster.children.append(nodes[int(output_linkage[i,0])])
			cur_cluster.children.append(nodes[int(output_linkage[i,1])])
			nodes.append(cur_cluster)
			
		res = nodes[len(nodes)-1]
		res.regenerate_not_exported(items)
		
		
		print_verbose(3, 'Clustering result: ' +str(res))
		
		return res
		
		
		
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
		
		
	