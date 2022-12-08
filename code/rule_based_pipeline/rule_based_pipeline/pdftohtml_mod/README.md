Please note:

* For running this on a Windows Machine, pdftohtml_mod.exe should be used. All libraried are included as DLL files.
* For running this on a Ubuntu/Linux Machine, pdftohtml_mod should be used. Note that some libraries should be installed (FreeType, libpng, zlib ).
* If you want or need to compile the pdftohtml tool yourself, please follow the instructions as described in INSTALL in the zip file xpdf-4.02_mod.zip. Then, use the pdftohtml executable file that has been built (from the build/xpdf directory).

The correct path to this file must be set in the Python file HTMLDirectory.py around line 25:

	@staticmethod
	def call_pdftohtml(infile, outdir):
		print_verbose(2, '-> call pdftohtml_mod '+infile)
		os.system('pdftohtml_mod\pdftohtml_mod.exe "' + infile + '" "' + remove_trailing_slash(outdir) + '"')  ## TODO: Specify correct path here!



DO NOT use the original xpdfreader tool, because I made some modifications to the source code, which are needed for the table detection algorithm and protected PDFs to work properly.
