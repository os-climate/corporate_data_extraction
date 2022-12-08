# ============================================================================================================================
# PDF_Analyzer
# File   : Format_Analyzer.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
# ============================================================================================================================

from globals import *


		
class Format_Analyzer:
	#pattern_numeric = re.compile(r'^(-?[ ]*[0-9]*(,[0-9][0-9][0-9])*(\.[0-9]+)?|-?[ ]*[0-9]*(\.[0-9][0-9][0-9])*(,[0-9]+)?)$')
	#pattern_numeric = re.compile(r'^\(?(-?\(?[ ]*[0-9]*(,[0-9][0-9][0-9])*(\.[0-9]+)?|-?[ ]*[0-9]*(\.[0-9][0-9][0-9])*(,[0-9]+)?)\)?$')
	pattern_numeric = re.compile(r'^\(?(-?\(?[ ]*[0-9]*(,[0-9][0-9][0-9])*(\.[0-9]+)?|-?[ ]*[0-9]*(\.[0-9][0-9][0-9])*(,[0-9]+)?)\)?(\*?)*$') #by Lei
	pattern_numeric_multi = re.compile(r'^(\(?(-?\(?[ ]*[0-9]*(,[0-9][0-9][0-9])*(\.[0-9]+)?|-?[ ]*[0-9]*(\.[0-9][0-9][0-9])*(,[0-9]+)?)\)?)+$')
	#pattern_year = re.compile(r'^(19[8-9][0-9]|20[0-9][0-9])$') #1980-2099
	pattern_year = re.compile(r'^[^0-9]*(19[8-9][0-9](/[0-9][0-9])?|20[0-9][0-9](/[0-9][0-9])?)[^0-9]*$') #1980-2099 #by Lei
	pattern_year_extended_1 = re.compile(r'^.*[0-3][0-9](\.|\\|/)[0-3][0-9](\.|\\|/)(19[8-9][0-9]|20[0-9][0-9]).*$') #1980-2099
	pattern_year_extended_2 = re.compile(r'^.*(19[8-9][0-9]|20[0-9][0-9])(\.|\\|/)[0-3][0-9](\.|\\|/)[0-3][0-9].*$') #1980-2099

	pattern_year_in_txt = re.compile(r'(19[8-9][0-9]|20[0-9][0-9])') #1980-2099
	pattern_null = re.compile(r'^(null|n/a|na|-*|\.*|,*|;*)$')
	pattern_whitespace = re.compile("^\s+|\s+$")
	pattern_ends_with_full_stop = re.compile(".*\.$")
	pattern_pagenum = re.compile(r'^[0-9]{1,3}$')
	pattern_non_numeric_char = re.compile(r'[^0-9\-\.]')
	pattern_file_path = re.compile(r'(.*/)(.*)\.(.*)')
	pattern_cleanup_text = re.compile(r'[^a-z ]')
	
	pattern_cleanup_filename = re.compile(r'(\[|\]|\(|\))')
	
	pattern_footnote = re.compile(r'[0-9]+\).*')
	
	
	@staticmethod
	def trim_whitespaces(val):
		return re.sub(Format_Analyzer.pattern_whitespace, '', val)
		
	
	@staticmethod
	def looks_numeric(val):
		#return Format_Analyzer.pattern_numeric.match(val.replace(' ', '').replace('$', '')) and len(val)>0
		val0 = remove_bad_chars(val, ' ()$%')
		#return Format_Analyzer.pattern_numeric.match(val0) and len(val0)>0
		return Format_Analyzer.pattern_numeric.match(val0.replace('WLTP', '')) and len(val0)>0 #by Lei

	@staticmethod
	def looks_numeric_multiple(val):
		#return Format_Analyzer.pattern_numeric.match(val.replace(' ', '').replace('$', '')) and len(val)>0
		return Format_Analyzer.pattern_numeric_multi.match(remove_bad_chars(val, ' ()$%')) and len(val)>0

	@staticmethod
	def looks_weak_numeric(val):
		num_numbers = sum(c.isnumeric() for c in val)
		return num_numbers > 0

	@staticmethod
	def looks_percentage(val):
		return looks_weak_numeric(val) and '%' in val
		
	@staticmethod
	def to_year(val):
#		val0 = remove_bad_chars(val, 'FY') #by Lei
		val0 = re.sub(r'[^0-9]', '', val) #by Lei
		return int(val0) #by Lei
#		val0=remove_letter_before_year(val)
#		return int(val0.replace(' ', ''))

	@staticmethod
	def looks_year(val):
		return Format_Analyzer.pattern_year.match(val.replace(' ', ''))

	@staticmethod
	def looks_year_extended(val): #return year if found, otherwise None
		if(Format_Analyzer.pattern_year_extended_1.match(val.replace(' ', ''))):
			return int(Format_Analyzer.pattern_year_extended_1.match(val.replace(' ', '')).groups()[2])
		if(Format_Analyzer.pattern_year_extended_2.match(val.replace(' ', ''))):
			return int(Format_Analyzer.pattern_year_extended_2.match(val.replace(' ', '')).groups()[0])
		if(Format_Analyzer.looks_year(val)):
			return Format_Analyzer.to_year(val)
		
		return None

		
	@staticmethod
	def cleanup_number(val):
		s = re.sub(Format_Analyzer.pattern_non_numeric_char, '' , val)
		# filter out extra dots
		first_dot = s.find('.')
		if(first_dot == -1):
			return s
			
		return s[0:first_dot+1] + s[first_dot+1:].replace('.', '')
	
	@staticmethod	
	def to_int_number(val, limit_chars=None):
		s = Format_Analyzer.cleanup_number(val)
		if(s == ''):
			return None
		return int(float(s if limit_chars is None else s[0:limit_chars]))
		
	@staticmethod	
	def to_float_number(val, limit_chars=None):
		s = Format_Analyzer.cleanup_number(val)
		if(s == ''):
			return None
		return float(s)
		
	@staticmethod
	def cleanup_text(val): #remove all characters except letters and spaces
		return re.sub(Format_Analyzer.pattern_cleanup_text, '', val)
		

	@staticmethod
	def looks_null(val):
		return Format_Analyzer.pattern_null.match(val.replace(' ', '').lower())

	@staticmethod
	def looks_words(val):
		num_letters = sum(c.isalpha() for c in val)
		return num_letters > 5

	@staticmethod
	def looks_weak_words(val):
		num_letters = sum(c.isalpha() for c in val)
		num_numbers = sum(c.isnumeric() for c in val)
		return num_letters > 2 and num_letters > num_numbers

	@staticmethod
	def looks_weak_non_numeric(val):
		num_letters = sum(c.isalpha() for c in val)
		num_numbers = sum(c.isnumeric() for c in val)
		num_others = len(val) - (num_letters + num_numbers)
		#return (num_letters + num_others > 1) or (num_letters + num_others > num_numbers)
		#return (num_letters + num_others > 1 and num_numbers < (num_letters + num_others) * 2 + 1) or (num_letters + num_others > num_numbers) 
		return num_letters > 0 and num_letters > num_numbers and ((num_letters + num_others > 1 and num_numbers < (num_letters + num_others) * 2 + 1) or (num_letters + num_others > num_numbers))

	@staticmethod
	def looks_other_special_item(val):
		return len(val) < 4 and not Format_Analyzer.looks_words(val) and not Format_Analyzer.looks_numeric(val)
		
		

	@staticmethod
	def looks_pagenum(val):
		return Format_Analyzer.pattern_pagenum.match(val.replace(' ', '')) and len(val)>0 and val.replace(' ', '') != '0'
		
	@staticmethod
	def looks_running_text(val):
		txt = Format_Analyzer.trim_whitespaces(val)
		num_full_stops = txt.count(".")
		num_comma = txt.count(",")
		num_space = txt.count(" ")
		ends_with_full_stop = True if Format_Analyzer.pattern_ends_with_full_stop.match(txt) else False
		txtlen = len(txt)
		num_letters = sum(c.isalpha() for c in txt)
		if(num_letters<20):
			return False #too short
		if(num_letters / txtlen < 0.5):
			return False #strange: less than 50% are letters
		if(num_space < 5):
			return False #only 5 words or less
		if(num_comma / txtlen < 0.004 and num_full_stops / txtlen < 0.002):
			return False #too few commans / full stops
		if(ends_with_full_stop):
			#looks like a sentence
			return True
		
		#does not end with full stop, so we require more conditons to hold
		return ((num_full_stops > 2) or \
		       (num_full_stops > 1 and num_comma > 1)) and \
			   (num_letters > 30) and \
			   (num_space > 10)

			   
			   
	@staticmethod
	def looks_footnote(val):
		return Format_Analyzer.pattern_footnote.match(val.replace(' ', '').lower())
			   
	@staticmethod
	def exclude_all_years(val):
		return re.sub(Format_Analyzer.pattern_year, '' , val)
		
		
	@staticmethod
	def extract_file_path(val):
		return Format_Analyzer.pattern_file_path.match(val).groups()
		
	@staticmethod
	def extract_file_name(val):
		fp = Format_Analyzer.extract_file_path('/'+val.replace('\\','/'))
		return fp[1] + '.' + fp[2]
		
	@staticmethod
	def cleanup_filename(val):
		return re.sub(Format_Analyzer.pattern_cleanup_filename, '_', val)
		
	@staticmethod
	def extract_year_from_text(val):
		lst = list(set(re.findall(Format_Analyzer.pattern_year_in_txt, val)))
		if(len(lst) == 1):
			return int(lst[0])
		return None # no or multiple results
		
		
	@staticmethod
	def cnt_overlapping_items(l0, l1):
		return len(list(set(l0) & set(l1)))
		