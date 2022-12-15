# INCEpTION to Pandas
## Purpose:

Tool to transform the KPI answers layer via UIMA CAS XMI (XML 1.1) into a structured
format. In the moment we export everything to excel, but the data is stored internally 
in a pandas data frame and can therefore be transferred to any pandas export supported
type.

## Prerequisites:

* check requirements.txt for libraries
* check settings.json for settings. 
    Make sure you have writing rights on all directories
* Hardware: 
	* Folder for storing the input and output
	* Normal CPU enough

## Process:

* First you have to export the annotations from INCEpTION in a UIMA CAS XMI (XML 1.1)
  format (example: Test.zip). The zip file has to be extracted (not yet supported 
  within the code, but maybe in a next version) and the files have to be placed into
  the input folder (specified in settings.json) into a separate folder (example: folder
  Test, which contains two files Test.xmi and TypeSystem.xml).
* Next run the code. The code will use dkpro-cassis python package to load the 
  UIMA format. We used version 0.7.2, but just because that was the newest version
  at the time when the code was initially set up. Note that we changed select_covering
  for our purpose to also get partially annotated sentences.
* The code will process all folders in the input folder one-by-one and transfer the 
  respective folder into the output folder (specified in settings.json) enhanced with 
  one excel file. One folder is processed in under one second.
  
NOTE: The annotation can be over multiple lines and paragraphs, but not over multiple 
pages. This is due to the fact, that also the ML Machine is not capable of using this
in the moment.
 
## Input Parameter:

There are no parameter. All paths are stored in settings.json.

## Output

| KPI     | ANSWER| TYPE |ANSWER_X |ANSWER_Y | PAGE | PAGE_WIDTH |PAGE_HEIGHT|PAGE_ORIENTATION|COV_SENTENCES|PDF_NAME|
|:-------    |:---------|:--------|:------|:------|:----------|:---------|:---------|:---------|:---------|:---------|
|13 - Total Scope 1/2 |	actions |	KPIAnswer|	151.68173|	191.6489|	1|	612|792|	0|	"We are very clear that it is not sufficient for Shell’s actions and behaviour merely to be legally sound."|	Test.pdf|


* KPI: KPI selected from the KPIs tagset
* ANSWER: Answer which was annotated
* TYPE: For now this is always KPIAnswer, but maybe in the future more is needed
* ANSWER_X: x coordinate of the answer 
* ANSWER_Y: y coordinate of the answer
* PAGE: Page number starting at 0
* PAGE_WIDTH: Total width of the page
* PAGE_HEIGHT: Total height of the page
* PAGE_ORIENTATION: Orientation of the original pdf: Portrait is 0
* COV_SENTENCES: All sentences which are full or partially annotated are extracted.
* PDF_NAME: Name of the pdf which was annotated

## Unittest:

There is no unittest for this code. Maybe one can add one in a future release.

## Additional information

* The files layer.json and tagsets.json are need in the INCEpTION tool. Just go to 
settings and upload into tagsets the tagsets.json and into layers the layer.json. 
Afterwards the KPIAnswers Tag will be available when you annotate pdfs.
* In the code we have changed select_covering for our purpose to also get 
partially annotated sentences.
