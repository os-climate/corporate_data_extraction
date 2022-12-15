# ============================================================================================================================
# PDF_Analyzer
# File   : TestData.py
# Author : Ismail Demir (G124272)
# Date   : 02.08.2020
# ============================================================================================================================

from TestDataSample import *
from Format_Analyzer import *
from KPIResultSet import *
from DataImportExport import *


class TestData:

	samples = None
	
	SRC_FILE_FORMAT_AUTO = 0
	SRC_FILE_FORMAT_OLD = 1
	SRC_FILE_FORMAT_NEW = 2

	def __init__(self):
		self.samples = []
		
	def filter_kpis(self, by_kpi_id = None, by_data_type = None, by_source_file = None, by_has_fixed_source_file = False):
		samples_new = []
		for s in self.samples:
			keep = True
			if(by_kpi_id is not None and s.data_kpi_id not in by_kpi_id):
				keep = False
			if(by_data_type is not None and s.data_data_type not in by_data_type):
				keep = False
			if(by_has_fixed_source_file and s.fixed_source_file is None):
				keep = False
			if(by_source_file is not None and s.data_source_file not in by_source_file):
				keep = False
			
			if(keep):
				samples_new.append(s)
		
		self.samples = samples_new
				
	
	def get_pdf_list(self):
		res = []
		for s in self.samples:
			res.append(s.data_source_file)
		res = list(set(res))
		res = sorted(res, key=lambda s: s.lower())
		return res

	def get_fixed_pdf_list(self):
		res = []
		for s in self.samples:
			res.append(s.fixed_source_file)
		res = list(set(res))
		res = sorted(res, key=lambda s: s.lower())
		return res
		
		
	def fix_file_names(self, fix_list):
		for i in range(len(self.samples)):
			for f in fix_list:
				if(self.samples[i].data_source_file == f[0]):
					self.samples[i].fixed_source_file = f[1]
					break
					
		
		
	def load_from_csv(self, src_file_path, src_file_format = SRC_FILE_FORMAT_AUTO):
	
	
		raw_data = ''
	
		def read_next_cell(p):
			p0 = -1
			p1 = -1
			p2 = -1
			#print("====>> p = "+str(p))
			if(raw_data[p:(p+4)]  == '"[""'):
				p0 = p + 4
				p1 = raw_data.find('""]"', p+1)
				p2 = p1 + 4
			elif(raw_data[p] == '"'):
				p0 = p+1
				p_cur = p0
				while(True):
					p1 = raw_data.find('"', p_cur)
					if(raw_data[p1+1]!='"'):
						break
					p_cur = p1 + 2
				
				p2 = p1 + 1
			else:
				p0 = p
				p2_a = raw_data.find(',' if  src_file_format == TestData.SRC_FILE_FORMAT_OLD else ';' ,p)
				p2_b = raw_data.find('\n',p)
				if(p2_a == -1):
					p2 = p2_b
				elif(p2_b == -1):
					p2 = p2_a
				else:
					p2 = min(p2_a, p2_b)
				
				p1 = p2
				#print("===>> p1="+str(p1))
			
			if(p1 == -1 or raw_data[p2] not in (',' if  src_file_format == TestData.SRC_FILE_FORMAT_OLD else ';', '\n')):
				raise ValueError('No cell delimiter detected after position ' +str(p) + ' at "'+raw_data[p:p+20]+'..."')
				
			
			cell_data = raw_data[p0:p1].replace('\n', ' ')
			#print("===>>>" + cell_data)
			
			return cell_data, p2+1, raw_data[p2] == '\n'
			
		def read_next_row(p, n):
			res = []
			for i in range(n):
				cell_data, p, is_at_end = read_next_cell(p)
				if(i==n-1):
					if(not is_at_end):
						raise ValueError('Row has not ended after position ' +str(p) + ' at "'+raw_data[p:p+20]+'..."')
				else:
					if(is_at_end):
						raise ValueError('Row has ended too early after position ' +str(p) + ' at "'+raw_data[p:p+20]+'..."')
				res.append(cell_data)
			
			#print('==>> next row starts at pos '+str(p)  + ' at "'+raw_data[p:p+20]+'..."')
			return res, p
				
	
		if(src_file_format == TestData.SRC_FILE_FORMAT_AUTO):
			try:
				#try old format:
				print_verbose(2, 'Trying old csv format')
				return self.load_from_csv(src_file_path, TestData.SRC_FILE_FORMAT_OLD)
			except ValueError:
				#try new format:
				print_verbose(2, 'Trying new csv format')
				return self.load_from_csv(src_file_path, TestData.SRC_FILE_FORMAT_NEW)
				
				
	
		self.samples = []
	
		with open(src_file_path, errors='ignore', encoding="ascii") as f:
			data_lines = f.readlines()
			
		
		#print(len(data_lines))
		
		for i in range(len(data_lines)):
			data_lines[i] = data_lines[i].replace('\n', '')
		
		raw_data = '\n'.join(data_lines[1:]) + '\n'
		
		# current format in sample csv file (old-format): 
		# Number,Sector,Unit,answer,"comments, questions",company,data_type,irrelevant_paragraphs,kpi_id,relevant_paragraphs,sector,source_file,source_page,year
		
		# and for new format:
		# Number;company;source_file;source_page;kpi_id;year;answer;data_type;relevant_paragraphs;annotator;sector;comments
		
		p = 0
		
		while(p  < len(raw_data)):
		
			if(src_file_format == TestData.SRC_FILE_FORMAT_OLD):
				# parse next row
				row_data, p = read_next_row(p, 14)
				#print(row_data)

				year = Format_Analyzer.to_int_number(row_data[13], 4)
				if(not Format_Analyzer.looks_year(str(year))):
					raise ValueError('Found invalid year "' +str(year) +'" at row ' + str(row_data))
				
				sample = TestDataSample()
				sample.data_number 				   = Format_Analyzer.to_int_number(row_data[0])   #0
				sample.data_sector                 = row_data[1]   #''
				sample.data_unit                   = row_data[2]   #''
				sample.data_answer                 = row_data[3]   #''
				sample.data_comments_questions     = row_data[4]   #''
				sample.data_company                = row_data[5]   #''
				sample.data_data_type              = row_data[6]   #''
				sample.data_irrelevant_paragraphs  = row_data[7]   #''
				sample.data_kpi_id                 = Format_Analyzer.to_int_number(row_data[8])   #0
				sample.data_relevant_paragraphs    = row_data[9]   #''
				sample.data_sector                 = row_data[10]   #''
				sample.data_source_file            = row_data[11]   #''
				sample.data_source_page            = Format_Analyzer.to_int_number(row_data[12])   #0
				sample.data_year                   = year   #0
				
				self.samples.append(sample)
				
			if(src_file_format == TestData.SRC_FILE_FORMAT_NEW):
				# parse next row
				row_data, p = read_next_row(p, 12)
				#print(row_data)

				year = Format_Analyzer.to_int_number(row_data[5], 4)
				if(not Format_Analyzer.looks_year(str(year))):
					raise ValueError('Found invalid year "' +str(year) +'" at row ' + str(row_data))
				
				sample = TestDataSample()
				sample.data_number 				   = Format_Analyzer.to_int_number(row_data[0])   #0
				sample.data_sector                 = row_data[10]   #''
				sample.data_unit                   = 'N/A'
				sample.data_answer                 = row_data[6]   #''
				sample.data_comments_questions     = row_data[11]   #''
				sample.data_company                = row_data[1]   #''
				sample.data_data_type              = row_data[7]   #''
				sample.data_irrelevant_paragraphs  = 'N/A'
				sample.data_kpi_id                 = Format_Analyzer.to_float_number(row_data[4])   #0
				sample.data_relevant_paragraphs    = row_data[8]   #''
				sample.data_source_file            = row_data[2]   #''
				sample.data_source_page            = Format_Analyzer.to_int_number(row_data[3])   #0
				sample.data_year                   = year   #0
				
				self.samples.append(sample)
				
	def generate_dummy_test_data(self, pdf_folder, filter = '*'):
		def ext(f):
			res = [f]
			res.extend(Format_Analyzer.extract_file_path(f)) 
			return res
			
		file_paths = glob.glob(pdf_folder + '/**/' + filter + '.pdf', recursive=True)
		file_paths = [ext(f.replace('\\','/'))  for f in file_paths] #unixize all file paths
		
		cnt = 0
		for f in file_paths:
			fname = f[2] + '.' + f[3]
			
			if(fname != Format_Analyzer.cleanup_filename(fname)):
				print("Warning: Bad filename: '" + fname + "' - this file will be skipped")
				continue
		
		
			sample = TestDataSample()
			sample.data_number 				   = cnt
			sample.data_sector                 = 'N/A'
			sample.data_unit                   = 'N/A'
			sample.data_answer                 = 'N/A'
			sample.data_comments_questions     = 'N/A'
			sample.data_company                = 'N/A'
			sample.data_data_type              = 'N/A'
			sample.data_irrelevant_paragraphs  = 'N/A'
			sample.data_kpi_id                 = 0
			sample.data_relevant_paragraphs    = 'N/A'
			sample.data_sector                 = 'N/A'
			sample.data_source_file            = fname
			sample.fixed_source_file           = fname
			sample.data_source_page            = 0
			sample.data_year                   = 1900
			
			self.samples.append(sample)
			
			cnt += 1
			
		DataImportExport.save_info_file_contents(file_paths)
				
		
		
	
	def save_to_csv(self, dst_file_path):
		save_txt_to_file(TestDataSample.samples_to_csv(self.samples), dst_file_path)
		
	
			
		
		
	
	
	
			
	def __repr__(self):
		return TestDataSample.samples_to_string(self.samples)
			
		
			
			
			
		
		
		
		