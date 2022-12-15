# ============================================================================================================================
# PDF_Analyzer
# File	 : main_find_xy.py
# Author : Lei Deng (D87HMXV) - reference mian.py 
# Date	 : 12.10.2022
# ============================================================================================================================

# TODO:
from globals import *
import argparse
from HTMLDirectory import *
from HTMLPage import *
from TestData import *
from test import *
import config
import re
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


def generate_dummy_test_data():

	test_data = TestData()
	test_data.generate_dummy_test_data(config.global_raw_pdf_folder, '*')
	
	return test_data

def analyze_pdf(pdf_file, pageNum, txt, info_file_contents, force_pdf_convert=False, force_parse_pdf=False, assume_conversion_done=False, do_wait=False):
	
	print_verbose(1, "Analyzing PDF: " +str(pdf_file))
	
	htmldir_path = get_html_out_dir(pdf_file)#get pdf  
	os.makedirs(htmldir_path, exist_ok=True) #ceate directory recursively
	
	reload_neccessary = True # why use this?
	
	dir = HTMLDirectory()
	if(not assume_conversion_done):
		#convert pdf to html
		print_big("Convert PDF to HTML", do_wait)
		if(force_pdf_convert or not file_exists(htmldir_path+'/index.html')):
			HTMLDirectory.convert_pdf_to_html(pdf_file, info_file_contents) #04.11.2022
		
		# parse and create json and png
		print_big("Convert HTML to JSON and PNG", do_wait)

		#dir = HTMLDirectory()
		if(force_parse_pdf or get_num_of_files(htmldir_path+'/jpage*.json') != get_num_of_files(htmldir_path+'/page*.html') ): 
			dir.parse_html_directory(get_html_out_dir(pdf_file), 'page*.html') # ! page*
			dir.render_to_png(htmldir_path, htmldir_path)
			dir.save_to_dir(htmldir_path)

				

	# load json files
	print_big("Load from JSON", do_wait)
	if(reload_neccessary):
		dir = HTMLDirectory() 
		dir.load_from_dir(htmldir_path, 'jpage*' + str(pageNum) + '.json')
	

	# get coordinates
	print_big("get coordinates", do_wait)
	res = []
	index = None
	this_id = 0
	for p in dir.htmlpages:
		#print_verbose(2, p.page_num)
		if(p.page_num == pageNum):
			for i in p.items:
				contxt = concat_Nitem(i,p)
				print_verbose(2, "\n\ncontxt:")
				print_verbose(2, contxt)
				try:
					print_verbose(2, "looking for: " + txt)
					index = contxt.index(txt) #get the index substing's first letter 
					wordIndex = len(contxt[:index].strip().split()) #get str before substring's 1st letter, split it by word，length = index of substring's 1st word
					print_verbose(2, "wordIndex:" )
					print_verbose(2, wordIndex)
					#print_verbose(2, "input txt:" + txt)
					res.extend((i.words[wordIndex].rect.get_coordinates()[0]/p.page_width,i.words[wordIndex].rect.get_coordinates()[1]/p.page_height))
					print_verbose(2, res)
					##### TODO: Also compare the paragraph from the CSV, in order to get the best result if we have multiple matches !!!
					return res
					#if(i.txt == txt):
					#res.extend(i.get_coordis()) #result[158.27,115.37]
				except ValueError:
					print_verbose(2, "substring not found")
				except IndexError:
					print_verbose(2, "list index out of range")
	return res
	
def concat_Nitem(item,page):
	res = item.txt
	cur_item = item
	while(cur_item.next_id != -1):
		for i in page.items:
			if(i.this_id == cur_item.next_id): #identify the next line of item
				res += ' ' + i.txt
				cur_item = i #update condition of while
				break
	return res.replace('\n', ' ')

def get_input_variable(val, desc):
	if val is None:
		val = input(desc)

	if(val is None or val==""):
		print_verbose(0, "This must not be empty")
		sys.exit(0)
	
	return val
	

# def read_csv(csv):
	# with open(csv) as csvFile: #open file
		# reader = csv.reader(csvFile) #buil csv reader
		# rows = [row for row in reader]
	# data = np.array(rows) #convert data format from list to array
	
def modify_csv(csv, info_file_contents):
	csvPD = pd.read_csv(csv, encoding='utf-8') #Building a csv reader
	coordis = None
	for c in range(len(csvPD)): #check columns
		#print(str(c) + str(csvPD['PDF_NAME'][c]))
		if str(csvPD['POS_X'][c])=="nan" or str(csvPD['POS_Y'][c]) == "nan":
			coordis = analyze_pdf(config.global_raw_pdf_folder + str(csvPD['PDF_NAME'][c]), int(csvPD['PAGE'][c]), str(csvPD['ANSWER_RAW'][c]), info_file_contents, assume_conversion_done=False, force_parse_pdf=False)
			print_verbose(2, "coord:")
			print_verbose(2, coordis)
			if(len(coordis)>0):
				csvPD['POS_X'][c] = coordis[0]
				csvPD['POS_Y'][c] = coordis[1]
			#df = pd.DataFrame(coordis, encoding = 'utf-8-sig') #initical data as dataframe
	csvPD.to_csv(csv, index=False)
	print_verbose(2, csvPD.to_csv(csv, index=False))




def main():

	#parse input parameters
	
	parser = argparse.ArgumentParser(description='coordinates extraction')

	parser.add_argument('--raw_pdf_folder',
						type=str,
						default=None,
						help='Folder where PDFs are stored')
	parser.add_argument('--working_folder',
						type=str,
						default=None,
						help='Folder where working files are stored')
	parser.add_argument('--pdf_name',
						type=str,
						default=None,
						help='name of pdf which you want to check')
	parser.add_argument('--csv_name',
						type=str,
						default=None,
						help='name of csv file')
	# parser.add_argument('--page_number',
						# type=int,
						# default=None,
						# help='in which page of pdf you want to find the coordinates of text')
	# parser.add_argument('--text',
						# type=str,
						# default=None,
						# help='for which text you want to find the coordinates')
	parser.add_argument('--output_folder',
						type=str,
						default=None,
						help='Folder where output is stored')
	parser.add_argument('--verbosity',
						type=int,
						default=1,
						help='Verbosity level (0=shut up)')	

	args = parser.parse_args()
	config.global_raw_pdf_folder = remove_trailing_slash(get_input_variable(args.raw_pdf_folder, "What is the raw pdf folder?")).replace('\\', '/') + r'/'
	config.global_working_folder = remove_trailing_slash(get_input_variable(args.working_folder, "What is the working folder?")).replace('\\', '/') + r'/'
	config.global_pdf_name = get_input_variable(args.pdf_name, "Which pdf do you want to check?") 
	config.global_csv_name = get_input_variable(args.csv_name, "Which csv file do you want to check?") 
	#config.global_page_number = get_input_variable(args.page_number, "Which page do you want to check?")
	#config.global_text = get_input_variable(args.text, "For which text do you want to find the x, y coordinates?")
	config.global_output_folder =  remove_trailing_slash(get_input_variable(args.output_folder, "What is the output folder?")).replace('\\', '/') + r'/'
	config.global_verbosity = args.verbosity
	
	os.makedirs(config.global_working_folder, exist_ok=True)
	os.makedirs(config.global_output_folder, exist_ok=True)
	
	# fix config.global_exec_folder and config.global_rendering_font_override
	path = ''
	try:
		path = globals()['_dh'][0]
	except KeyError:
		path = os.path.dirname(os.path.realpath(__file__))
	path = remove_trailing_slash(path).replace('\\', '/')
	
	config.global_exec_folder = path+ r'/'
	config.global_rendering_font_override = path + r'/' + config.global_rendering_font_override
	
	print_verbose(1, "Using config.global_exec_folder=" + config.global_exec_folder)
	print_verbose(1, "Using config.global_raw_pdf_folder=" + config.global_raw_pdf_folder)
	print_verbose(1, "Using config.global_working_folder=" + config.global_working_folder)
	print_verbose(1, "Using config.global_output_folder=" + config.global_output_folder)
	print_verbose(1, "Using config.global_verbosity=" + str(config.global_verbosity))
	print_verbose(5, "Using config.global_rendering_font_override=" + config.global_rendering_font_override)

	test_data = generate_dummy_test_data()
	
	print_big("Data-set", False)
	print_verbose(1, test_data)


	
	
	info_file_contents = DataImportExport.load_info_file_contents(remove_trailing_slash(config.global_working_folder) + '/info.json')
	
	time_start = time.time()
	

	coordisresults = []
	#cur_coordisresults = analyze_pdf(config.global_raw_pdf_folder + config.global_pdf_name, config.global_page_number,	 config.global_text, info_file_contents, assume_conversion_done=False, force_parse_pdf=False) #analyse input data
	modify_csv(config.global_csv_name, info_file_contents)
	#print(cur_coordisresults) #debugging	empty， so analyze_pdf method didn't work as expected
	#coordisresults.extend(cur_coordisresults)
	#print(coordisresults) #debugging	empty
	print_verbose(1, "RESULT FOR " + config.global_pdf_name)
	print_verbose(1, coordisresults)

		
	time_finish = time.time()
	
	total_time = time_finish - time_start
	
main()	

