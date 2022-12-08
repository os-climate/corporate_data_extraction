# ============================================================================================================================
# PDF_Analyzer
# File   : globals.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
# ============================================================================================================================
# -*- coding: utf-8 -*-

import re
import sys, codecs
from datetime import datetime
import os, glob
import argparse
from PIL import Image, ImageDraw, ImageFont
from copy import deepcopy
import time
import statistics
import json
import jsonpickle
import html
import shutil
import config
import math


ALIGN_DEFAULT 			= 0
ALIGN_LEFT 				= 1
ALIGN_RIGHT 			= 2
ALIGN_CENTER 			= 3 # New-27.06.2022


#Text categories
CAT_DEFAULT				= 0
CAT_RUNNING_TEXT		= 1
CAT_HEADLINE			= 2
CAT_OTHER_TEXT			= 3
CAT_TABLE_DATA			= 4
CAT_TABLE_HEADLINE		= 5
CAT_TABLE_SPECIAL		= 6 #e.g., annonations
CAT_MISC				= 7 #probably belongs to figures
CAT_FOOTER				= 8 #bugfix 26.07.2022
CAT_FOOTNOTE			= 9 #new categorie for finding footnotes

# Other constants
DEFAULT_VTHRESHOLD					= 15.0 / 609.0 #609px is sample page width
DEFAULT_SPECIAL_ITEM_MAX_DIST		= 15.0 / 609.0 #609px is sample page width
DEFAULT_HTHROWAWAY_DIST 			= 0.3
DEFAULT_SPECIAL_ITEM_CUTOFF_DIST 	= 15.0 / 609.9 #609px is sample page width
DEFAULT_FLYSPECK_HEIGHT				= 3.0 / 841.0 #841.0 is sampe page height


# Rendering options
RENDERING_USE_CLUSTER_COLORS	= False


# Workaround for redirecting PRINT to STDOUT (use it, if you get an error message)
if sys.stdout.encoding != 'utf-8':
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
  sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
  
	
def wait_for_user():
	input("Press Enter to continue...")

	
def print_big(txt, do_wait = True):
	if(config.global_verbosity == 0):
		return
	if(do_wait):
		wait_for_user()
	print("=======================================")
	print(txt.upper())
	print("=======================================")	
	if(do_wait):
		wait_for_user()


		
def print_verbose(verbosity, txt):
	if(verbosity <= config.global_verbosity):
		print(str(txt))
		
def print_subset(verbosity, list, subset):
	for s in subset:
		print_verbose(verbosity, list[s])
		

def file_exists(fname):
	return os.path.isfile(fname)
	
def get_num_of_files(pattern):
	return len(glob.glob(pattern))
	
def remove_trailing_slash(s):
	if(s.endswith('/') or s.endswith('\\')):
		s = s[:-1]
	return s	

def remove_bad_chars(s, c): #removed all occurences of c in s
	res = s
	for x in c:
		res = res.replace(x, '')
	return res
		
def dist(x1,y1,x2,y2):
	return ((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))**0.5

def get_text_width(text,  font):
	size = font.getsize(text)
	return size[0]

def get_html_out_dir(fname):
	fname = '/'+ fname.replace('\\','/')
	return config.global_working_folder + r'html/' + fname[(fname.rfind(r'/')+1):] + r'.html_dir' 
	
	
	
def analyze_pdf(fname):
	pdf_to_html(fname , get_html_out_dir(fname))			
	
def save_txt_to_file(txt, fname):
	with open(fname, "w", encoding="utf-8") as text_file:
		text_file.write(txt)

	
def hsv_to_rgba(h, s, v): #h,s,v in [0,1], result r,g,b,a in [0,256)
	if s == 0.0: return (v, v, v)
	i = int(h*6.) # XXX assume int() truncates!
	f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
	if i == 0: return (int(255*v), int(255*t), int(255*p), 255)
	if i == 1: return (int(255*q), int(255*v), int(255*p), 255)
	if i == 2: return (int(255*p), int(255*v), int(255*t), 255)
	if i == 3: return (int(255*p), int(255*q), int(255*v), 255)
	if i == 4: return (int(255*t), int(255*p), int(255*v), 255)
	if i == 5: return (int(255*v), int(255*p), int(255*q), 255)		