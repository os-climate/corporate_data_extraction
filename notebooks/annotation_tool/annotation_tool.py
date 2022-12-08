import pandas as pd
from IPython.display import display, Markdown
import ipywidgets as widgets
import glob
import numpy as np

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_colwidth', None)

company = 'Imperial Oil Ltd'
year = 2018
sector = "OG"
annotator = 'Max'
annotation_path = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL'
output_path = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/output'
input_path = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/input'
kpi_mapping_fpath = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/kpi_mapping.csv'
df_result = pd.read_excel(annotation_path + "/annotations.xlsx")

kpi_of_interest_textarea = widgets.Textarea(
        placeholder='Insert KPIs as a comma seperated list, e.g. 0, 1, 2, 3.1, ...',
        layout = widgets.Layout(width='50%'),
        style = {'description_width': 'initial'},
        description='KPI of interest:',
        disabled=False
        )

report_to_analyze_select =  widgets.Select(
     #   options=None, #sorted(select_options, reverse=True),
        description='Available results:',
        style = {'description_width': 'initial'},
        layout = widgets.Layout(width='100%', height='150px'),
        disabled=False
        ) 

kpi_to_analyze_dropdown = widgets.Dropdown(
      #  options= None, #sorted(options_kpi),
        # rows=10,
        value = None,
        description='Current KPI:',
        style = {'description_width': 'initial'},
        layout = widgets.Layout(width='100%')
        )

answer_select =  widgets.SelectMultiple(
     #   options=None, #sorted(select_options, reverse=True),
        description='Correct answer',
        style = {'description_width': 'initial'},
        #layout = widgets.Layout(width='50%', height='150px'),
        disabled=False
        ) 

paragraph_select =  widgets.SelectMultiple(
     #   options=None, #sorted(select_options, reverse=True),
        description='Correct paragraph',
        style = {'description_width': 'initial'},
        #layout = widgets.Layout(width='50%', height='150px'),
        disabled=False
        ) 
    
answer_dropdown = widgets.Dropdown(
        description="Choose rank of correct kpi:", 
       # options=None, 
        style = {'description_width': 'initial'},
        layout = widgets.Layout(width='50%'),
        value = None
        )

paragraph_dropdown = widgets.Dropdown(
        description="Choose rank of correct pagraph:", 
   #     options=None, 
        style = {'description_width': 'initial'},
        layout = widgets.Layout(width='50%'),
        value = None
        )

correct_answer_textarea = widgets.Textarea(
        value='',
        placeholder='Enter your correction.',
        layout = widgets.Layout(width='60%'),
        description='Correction:',
        disabled=False
        )

correct_paragraph_textarea = widgets.Textarea(
        value='',
        placeholder='Enter your correction.',
        layout = widgets.Layout(width='60%'),
        description='Correction:',
        disabled=False
        )

use_button = widgets.Button(
        value=False,
        description='Use',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Use the previous defined kpis of interest',
        icon='check' # (FontAwesome names without the `fa-` prefix)
        )

save_button = widgets.Button(
        value=False,
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Save current annotation and switch to next KPI',
        icon='check' # (FontAwesome names without the `fa-` prefix)
        )


output_kpi_of_interest = widgets.Output()
output_pdf_selection = widgets.Output()
output_annotation = widgets.Output()
output_save = widgets.Output()

def get_kpi_overview():
    kpi_mapping_df = pd.read_csv(kpi_mapping_fpath)
    kpi_mapping_df['kpi_id'] = kpi_mapping_df['kpi_id'].map('{:g}'.format)
    filtered_columns = kpi_mapping_df.columns[~kpi_mapping_df.columns.str.contains('Unnamed')]
    kpi_mapping_df = kpi_mapping_df[filtered_columns]
    return kpi_mapping_df
    

def get_kpi_of_interest(kpi_str=None):
    if kpi_str == None:
        kpis = "".join(kpi_of_interest_textarea.value.split())
    else:
        kpis= "".join(kpi_str.value.split())
    kpis = kpis.split(',')
   # kpis = list(map(float, kpis))
    return kpis

def update_pdf_selection(input_path, annotation_path, kpi_of_interest):
    global df_result
    selection = []
    outputs = glob.glob(input_path + "/*")
    outputs = [x.rsplit('/', 1)[1] for x in outputs]
    df_annotations = df_result
    kpis = set(map(float, set(kpi_of_interest)))
    for output in outputs:
        df_output = pd.read_csv(input_path + "/" + output)
        pdf_name = df_output['pdf_name'].values[0]
        df_annotations_temp = df_annotations[df_annotations.source_file == pdf_name]
        kpis_contained = [float(x) for x in df_annotations_temp['kpi_id'].values if x in kpis]
        if set(kpis_contained) == kpis:
            selection = selection + [(f'DONE  - ' + output, output)]
        else:
            selection = selection + [(f'TODO ({len(set(kpis_contained))}/{len(kpi_of_interest)}) - ' + output, output)]
    return sorted(selection, reverse=True) 


def get_df_for_selected_report():
    df_infer = pd.read_csv(input_path + "/" +  report_to_analyze_select.value) 
    df_kpi_mapping = pd.read_csv(kpi_mapping_fpath)[['kpi_id', 'question']]
    df = df_infer.merge(df_kpi_mapping, how='left', left_on='kpi', right_on = 'question')
    df = df[['kpi',	'kpi_id_y',	'answer','page','paragraph', 'source', 'score', 'no_ans_score', 'no_answer_score_plus_boost']]
    df = df.rename(columns={'kpi_id_y':'kpi_id'})
    return df

def get_answers_for_selected_kpi():
    if kpi_to_analyze_dropdown.value == None:
        kpis_of_interest = get_kpi_of_interest()
        kpi_id = min(kpis_of_interest)
    else:
        kpi_id = kpi_to_analyze_dropdown.value
    df = get_df_for_selected_report()
    df_filtered = df[df['kpi_id']==float(kpi_id)]
    return df_filtered


def update_rank_selection():
    df_answers =  get_answers_for_selected_kpi()
    index_list =  df_answers.index.values
    selection = []
    for i, x in enumerate(index_list):
        selection = selection + [(i+1,[i+1,x])]
    selection = selection + [('no correct answer',[-1,-1])]
    return selection

def use_button_on_click(b):
    kpis_of_interest = get_kpi_of_interest()
    try:
        kpi_of_interest = map(float, kpis_of_interest)
        with report_to_analyze_select.hold_trait_notifications():
            new_options = update_pdf_selection(input_path, annotation_path,  kpis_of_interest)
            report_to_analyze_select.options = new_options
        with kpi_to_analyze_dropdown.hold_trait_notifications():
            new_options = [(x,x) for x in kpis_of_interest]
            kpi_to_analyze_dropdown.values = kpis_of_interest
            kpi_to_analyze_dropdown.options = new_options
        output_kpi_of_interest.clear_output()
        with output_kpi_of_interest:
            display(kpi_of_interest_textarea)
            display(use_button)
            print('Your selected KPIs are: ' + " ".join(get_kpi_of_interest()))
            display(get_kpi_overview())
        output_pdf_selection.clear_output()
        with output_pdf_selection:
            display(report_to_analyze_select)
    except ValueError:
        output_kpi_of_interest.clear_output()
        with output_kpi_of_interest:
            display(kpi_of_interest_textarea)
            display(use_button)
            print('Kpi string has not the right format.')
            display(get_kpi_overview())
        
        
     #print(new_options)
   
    
def kpi_of_interest_handler(change):
    kpis_of_interest = get_kpi_of_interest()
     #print(new_options)
    with report_to_analyze_select.hold_trait_notifications():
        new_options = update_pdf_selection(input_path, annotation_path,  kpis_of_interest)
        report_to_analyze_select.options = new_options
    with kpi_to_analyze_dropdown.hold_trait_notifications():
        new_options = [(x,x) for x in kpi_of_interest]
        kpi_to_analyze_dropdown.values = kpis_of_interest
        kpi_to_analyze_dropdown.options = new_options
    output_pdf_selection.clear_output()
    with output_pdf_selection:
        display(report_to_analyze_select)


def report_to_analyze_handler(change):
    kpis_of_interest = get_kpi_of_interest()
    with kpi_to_analyze_dropdown.hold_trait_notifications():
        new_options = [(x,x) for x in kpis_of_interest]
        kpi_to_analyze_dropdown.value = min(kpis_of_interest)
        kpi_to_analyze_dropdown.options = new_options
    output_annotation.clear_output() 
    with output_annotation:
        print('\n')
        display(kpi_to_analyze_dropdown)
        display(get_answers_for_selected_kpi())
        

def kpi_to_analyze_handler(change):
    df_answers = get_answers_for_selected_kpi()
    with answer_dropdown.hold_trait_notifications():
        #answer_select.value = None
        new_rank_options = update_rank_selection()
        answer_dropdown.options = new_rank_options
    with paragraph_dropdown.hold_trait_notifications():
        #paragraph_select.value = None
        new_rank_options = update_rank_selection()
        paragraph_dropdown.options = new_rank_options    
        
    output_annotation.clear_output()
    with output_annotation:
        print('\n')
        display(kpi_to_analyze_dropdown)
        display(get_answers_for_selected_kpi())
        display(answer_dropdown) 
        display(paragraph_dropdown)
        #display(widgets.HBox([widgets.VBox([answer_dropdown, correct_answer_textarea]),widgets.VBox([paragraph_dropdown, correct_paragraph_textarea])]))
        
def answer_paragraph_handler(change):
    output_annotation.clear_output()
    with output_annotation:
        print('\n')
        display(kpi_to_analyze_dropdown)
        display(get_answers_for_selected_kpi())
        display(answer_dropdown) 
        if answer_dropdown.value[0] == -1:
            display(correct_answer_textarea)
        display(paragraph_dropdown)
        if paragraph_dropdown.value[0] == -1:
            display(correct_paragraph_textarea)

def build_annotation_entry():
    global df_result
    df2 = pd.DataFrame(data=None, columns=df_result.columns)
    id_correct_paragraph = paragraph_dropdown.value[1]
    rank_correct_paragraph = paragraph_dropdown.value[0]
    id_correct_answer =answer_dropdown.value[1]
    rank_correct_answer = answer_dropdown.value[0]
    correct_answer = correct_answer_textarea.value
    correct_paragraph = correct_paragraph_textarea.value
    kpi_to_investigate = kpi_to_analyze_dropdown.value
    df_output = get_df_for_selected_report()
    if paragraph_dropdown.value[1] == -1:
        paragraph = "[" + str(correct_paragraph) + "]"
        source_page = "[]" #+ str(correct_paragraph_page) +
        source = 'Text'   
        paragraph_pred_rank = -1
        paragraph_pred_score = -100
    else:
        paragraph = "[" + str(df_output.loc[id_correct_paragraph, 'paragraph']) + "]"
        source_page = "[" + str(df_output.loc[id_correct_paragraph, 'page']) + "]"
        source = df_output.loc[id_correct_paragraph, 'source']
        paragraph_pred_rank = rank_correct_paragraph
        paragraph_pred_score = 100
        
    if id_correct_answer == -1:
        answer = correct_answer
        kpi_pred_rank = -1
        kpi_pred_score = -100
        
    else:
        answer = df_output.loc[id_correct_paragraph, 'answer']
        kpi_pred_rank = rank_correct_answer
        kpi_pred_score = df_output.loc[df_output.index == id_correct_answer, 'score'].values[0]
        
    max_num = len(df_result)
   
    new_data = [max_num+1,
                company,
                report_to_analyze_select.value,
                source_page,
                kpi_to_investigate,
                year,
                answer,
                source,
                paragraph,
                annotator,
                sector,
                "",
               paragraph_pred_rank,
               paragraph_pred_score,
               kpi_pred_rank,
               kpi_pred_score]
    return new_data

def export_results():
    df_result.to_excel(annotation_path + "/annotations.xlsx", index=False)
    display('Success!')
    
    
def save_on_click(b):
    global df_result
     
    new_entry = build_annotation_entry()
    df_result.loc[len(df_result)] = new_entry
    
    kpis_of_interest = get_kpi_of_interest()
    val = kpi_to_analyze_dropdown.value
    index = kpis_of_interest.index(val)
    kpi_to_analyze_dropdown.value = kpis_of_interest[index + 1]
    
    output_save.clear_output()
    with output_save:
        display(save_button)
        print('Success!')
        display(df_result.tail(1))

    
def select_your_kpi_of_interest():
    kpi_overview = get_kpi_overview()
    output_kpi_of_interest.clear_output()
    with output_kpi_of_interest:
        display(kpi_of_interest_textarea)
        display(use_button)
        display(kpi_overview)
    
    use_button.on_click(use_button_on_click)
    display(output_kpi_of_interest)


def select_the_report_to_analyze():
    kpi_overview = get_kpi_overview()
    output_pdf_selection.clear_output()
    with output_pdf_selection:
        display(report_to_analyze_select)
    
    report_to_analyze_select.observe(report_to_analyze_handler, names='value')
    display(output_pdf_selection)
    
def lets_go():
   
    
    output_annotation.clear_output() 
    with output_annotation:
        print('\n')
        display(kpi_to_analyze_dropdown)
        display(get_answers_for_selected_kpi())
    output_save.clear_output() 
    with output_save:
        display(save_button)
        
    
        
    kpi_to_analyze_dropdown.observe(kpi_to_analyze_handler, names='value')
    kpi_to_analyze_handler('value')
    answer_dropdown.observe(answer_paragraph_handler, names='value')
    paragraph_dropdown.observe(answer_paragraph_handler, names='value')
    save_button.on_click(save_on_click)
    display(output_annotation)
    display(output_save)
   
