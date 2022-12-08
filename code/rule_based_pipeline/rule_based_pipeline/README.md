PREREQUISITES:

This tool runs by default on a Windows machine. For running it on Ubuntu (or other OS), please follow the instructions specified in README.md file, in the pdftohtml_mod directoy!

To run this tool, make sure that Python 3 and all required Python packages are installed (see requirements.txt).

============================================================

EXECUTION:

1. Place all PDFs in "raw_pdf/" subdirectory. If you want to use a different folder, then adjust the path for the input PDFs in globals.py (around line 26):
		global_raw_pdf_folder   = r"raw_pdf/" 
		
	For testing, you can use the Shell Sustainability Report 2019 as an example (https://reports.shell.com/sustainability-report/2019/servicepages/downloads/files/shell_sustainability_report_2019.pdf)

2. Run python main.py (or, python3 main.py depending on your setup)

3. You will see the output on the terminal, and it will also be saved in the subdirectory "test_data/" (in JSON and CSV format)


============================================================

REMARKS:

1. KPI defintions are for now in test.py (around line 60). This should be implemented in a better way in the future.
	#
	# Only used for initial testing
	#		
	def test_prepare_kpispecs():
		# TODO: This should be read from JSON files, but for now we can simply define it in code
		
		
2. To achieve different results / for debugging / different configurations, there are certain places in the code, marked
   with "### TODO:", in particular in the files main.py, globals.py, test.py. You can adjust the code here as documented.
   
3. There are also routines for evaluating the results against predefined training data. See "test_evaluation" in test.py, and TestEvaluation.py for more details.

4. In AnalyzerPage.py, you can specify which algorithms are used for analyzing PDFs in the function "find_kpis". 
   The most tested algorithm is the one for tables (around line 39):
		# 1. Tables
		for a in self.analyzer_table:
			res.extend(a.find_kpis(kpispecs))
			
	There is also a cluster based algorithm (fully implemented), but not well tested. So it is commented out for now.
	
5. The full integration of this tool into the corporate date pipeline still needs to be done. For now it can only be executed separately.