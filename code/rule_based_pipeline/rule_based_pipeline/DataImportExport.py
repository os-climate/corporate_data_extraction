# ============================================================================================================================
# PDF_Analyzer
# File   : DataImportExport.py
# Author : Ismail Demir (G124272)
# Date   : 05.08.2020
# ============================================================================================================================

from globals import *
from Format_Analyzer import *

class DataImportExport:

	@staticmethod
	def import_files(src_folder, dst_folder, file_list, file_type): 
		def ext(f):
			res = [f]
			res.extend(Format_Analyzer.extract_file_path(f)) 
			return res
	
		#print(src_folder)
		file_paths = glob.glob(src_folder + '/**/*.' + file_type, recursive=True)
		file_paths = [ext(f.replace('\\','/'))  for f in file_paths] #unixize all file paths
		
		res = []
		
		info_file_contents = {}
		
		for fname in file_list:
			fname_clean = fname.lower().strip() #(new)
			if(fname_clean[-4:]=='.'+file_type):
				fname_clean=fname_clean[:-4]
			
			#fname_clean = fname_clean.strip() (old)
			fpath = None
			
			# look case-sensitive
			for f in file_paths:
				if(f[2] + '.' + f[3] == fname):
					#match!
					fpath = f
					break
			
			
			
			# look case-insensitive
			if(fpath is None):
				for f in file_paths:
					#if(f[2].lower().strip() == fname_clean): (old)
					if(f[2].lower() == fname_clean):
						# match!
						fpath = f
						break
					
			#print('SRC: "' + fname + '" -> ' + str(fpath))
			new_file_name = None
			if(fpath is None):
				print_verbose(0, 'Warning: "' + fname + '" not found.')
			else:
				new_file_name = Format_Analyzer.cleanup_filename(fpath[2] + '.' + fpath[3])
				new_file_path = remove_trailing_slash(dst_folder) + '/' + new_file_name
				info_file_contents[new_file_path] = fpath[0]
				
				if(not file_exists(new_file_path)):
					print_verbose(1, 'Copy "' + fpath[0] + '" to "' + new_file_path + '"')
					shutil.copyfile(fpath[0], new_file_path)
				
				
				
			res.append((fname, new_file_name))
			
		#print(info_file_contents)
		
		#save info file contents:
		jsonpickle.set_preferred_backend('json')
		jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
		data = jsonpickle.encode(info_file_contents)
		f_info = open(remove_trailing_slash(config.global_working_folder) + '/info.json', "w")
		f_info.write(data)
		f_info.close()		
			
		return res
			
	
	@staticmethod
	def save_info_file_contents(file_paths):
		info_file_contents = {}
		
		for f in file_paths:
			info_file_contents[f[0]] = f[0]

		jsonpickle.set_preferred_backend('json')
		jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
		data = jsonpickle.encode(info_file_contents)
		f_info = open(remove_trailing_slash(config.global_working_folder) + '/info.json', "w")
		f_info.write(data)
		f_info.close()				
	
			
	@staticmethod
	def load_info_file_contents(json_file):
		f = open(json_file, "r")
		data = f.read()
		f.close()
		obj = jsonpickle.decode(data)
		return obj
		
		
				
			
		

			