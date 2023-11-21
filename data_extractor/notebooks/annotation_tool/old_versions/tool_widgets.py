"""
annotations_path = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL'
output_path = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/data/output'
input_path = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/data/input'
kpi_mapping_fpath = '/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/data/input/kpi_mapping.csv'
"""

import ipywidgets as widgets
import pandas as pd
from IPython.display import Markdown, display

annotations_path = "/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL"
output_path = "/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/output"
input_path = "/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/input"
kpi_mapping_fpath = "/opt/app-root/src/corporate_data_pipeline/NLP_ANNOTATION_TOOL/kpi_mapping.csv"
kpi_output = widgets.Output()
button_output = widgets.Output()
output = widgets.Output()
output_paragraph = widgets.Output()
layout_hidden = widgets.Layout(visibility="hidden")
layout_visible = widgets.Layout(visibility="visible", width="60%")
options_kpi = []
kpi_of_interest = []


def select_pdf_handler(change):
    global df_output
    df_output = pd.read_csv(output_path + "/" + str(select_pdf.value))
    pdf_name = df_output["pdf_name"].values[0]
    df_annotations_temp = df_annotations[df_annotations["source_file"] == pdf_name]
    kpis_contained = [x for x in df_annotations_temp["kpi_id"].values if x in kpi_of_interest]
    open_kpis = [x for x in kpi_of_interest if x not in kpis_contained]
    select_out.clear_output()
    with select_out:
        if len(open_kpis) > 1:
            print("The open kpi's are " + ", ".join([str(x) for x in open_kpis]) + ".")
        elif len(open_kpis) == 1:
            print("The open kpi is " + ", ".join([str(x) for x in open_kpis]) + ".")
        else:
            print("There are no open kpi's.")


def select_kpi_handler(change):
    global df_output
    global df_output_check
    kpi_to_investigate = select_kpi.value
    kpi = kpi_mapping_df.loc[kpi_mapping_df["kpi_id"] == kpi_to_investigate, "question"].values[0]
    df_output_check = df_output[df_output["kpi"] == kpi]
    global index_list
    global select_list
    index_list = df_output_check.index.values
    select_list = []
    for i, x in enumerate(index_list):
        select_list = select_list + [(i + 1, [i + 1, x])]
    select_list = select_list + [("no correct answer", [-1, -1])]
    dropdown.value = None
    w_dropdown_paragraph.value = None
    with dropdown.hold_trait_notifications():
        dropdown.options = select_list
    with w_dropdown_paragraph.hold_trait_notifications():
        w_dropdown_paragraph.options = select_list
    kpi_output.clear_output()
    with kpi_output:
        display(df_output_check)


def button_next_kpi_handler(b):
    global df_out
    global kpi_of_interest
    id_correct_paragraph = w_dropdown_paragraph.value[1]
    rank_correct_paragraph = w_dropdown_paragraph.value[0]
    id_correct_answer = dropdown.value[1]
    rank_correct_answer = dropdown.value[0]
    correct_answer = correct_answer_input.value
    correct_paragraph = correct_paragraph_input.value
    kpi_to_investigate = select_kpi.value
    df_temp = df_annotations.head(0)
    if w_dropdown_paragraph.value[1] == -1:
        paragraph = "[" + str(correct_paragraph) + "]"
        source_page = "[]"  # + str(correct_paragraph_page) +
        source = "Text"
        paragraph_pred_rank = -1
        paragraph_pred_score = -100
    else:
        paragraph = "[" + str(df_output.loc[id_correct_paragraph, "paragraph"]) + "]"
        source_page = "[" + str(df_output.loc[id_correct_paragraph, "page"]) + "]"
        source = df_output.loc[id_correct_paragraph, "source"]
        paragraph_pred_rank = rank_correct_paragraph
        paragraph_pred_score = 100
    if id_correct_answer == -1:
        answer = correct_answer
        kpi_pred_rank = -1
        kpi_pred_score = -100
    else:
        answer = df_output.loc[id_correct_paragraph, "answer"]
        kpi_pred_rank = rank_correct_answer
        kpi_pred_score = df_output.loc[df_output.index == id_correct_answer, "score"].values[0]

    try:
        max_num = np.max(df_out["number"].values)
    except ValueError:
        max_num = 1

    new_data = [
        max_num + 1,
        company,
        df_output_check["pdf_name"].values[0],
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
        kpi_pred_score,
    ]
    insert_annotation_into_df(df_out, new_data)
    # df_out.tail(1)
    kpi_output.clear_output()
    val = select_kpi.value
    index = kpi_of_interest.index(val)
    select_kpi.value = kpi_of_interest[index + 1]
    select_kpi_handler("value")
    button_output.clear_output()
    with button_output:
        display(df_out.tail(1))
        print("Success!")


def dropdown_kpi_eventhandler(change):
    output.clear_output()
    if dropdown.value == None:
        pass
    else:
        if dropdown.value[1] == -1:
            correct_answer_input.layout = layout_visible
        else:
            correct_answer_input.layout = layout_hidden
        with output:
            print("id_correct_answer: " + str(dropdown.value[1]))
            print("correct paragraph: " + str(w_dropdown_paragraph.value[1]))


def dropdown_paragraph_eventhandler(change):
    output.clear_output()
    if w_dropdown_paragraph.value == None:
        pass
    else:
        output_paragraph.clear_output()
        output.clear_output()
        with output_paragraph:
            display(w_dropdown_paragraph)
            if w_dropdown_paragraph.value[1] == -1:
                display(correct_paragraph_input)
        with output:
            print("id_correct_answer: " + str(dropdown.value[1]))
            print("id_correct_paragraph: " + str(w_dropdown_paragraph.value[1]))

            # Refactor and utility


def df_from_kpi_infer(infer_fpath, kpi_mapping_fpath):
    df_infer = pd.read_csv(infer_fpath)
    df_kpi_mapping = pd.read_csv(kpi_mapping_fpath)[["kpi_id", "question"]]
    df = df_infer.merge(df_kpi_mapping, how="left", left_on="kpi", right_on="question")
    df = df[
        [
            "pdf_name",
            "kpi",
            "kpi_id_y",
            "answer",
            "page",
            "paragraph",
            "source",
            "score",
            "no_ans_score",
            "no_answer_score_plus_boost",
        ]
    ]
    df = df.rename(columns={"kpi_id_y": "kpi_id"})
    return df


def get_answers_for_kpi_id(df, kpi_id):
    df_answers = df[df["kpi_id"] == kpi_id]
    return df_answers


def get_kpi_for_id(df, id):
    kpi = df["kpi_id"] == id
    return kpi


def get_kpi_selection_options(df):
    index_list = df.index.values
    select_list = []
    for i, x in enumerate(index_list):
        select_list = select_list + [(i + 1, [i + 1, x])]
    select_list = select_list + [("no correct answer", [-1, -1])]
    return select_list


def insert_annotation_into_df(df, new_entry):
    df.loc[len(df)] = new_entry


def build_annotation_entry(kpi_index, par_index, df, set_answer=None, set_pargraph=None, set_page=None):
    id_correct_paragraph = kpi_index
    rank_correct_paragraph = (par_index,)
    id_correct_answer = dropdown.value[1]
    rank_correct_answer = dropdown.value[0]
    correct_answer = correct_answer_input.value
    correct_paragraph = correct_paragraph_input.value
    kpi_to_investigate = select_kpi.value
    df_temp = df_annotations.head(0)
    if w_dropdown_paragraph.value[1] == -1:
        paragraph = "[" + str(correct_paragraph) + "]"
        source_page = "[]"  # + str(correct_paragraph_page) +
        source = "Text"
        paragraph_pred_rank = -1
        paragraph_pred_score = -100
    else:
        paragraph = "[" + str(df_output.loc[id_correct_paragraph, "paragraph"]) + "]"
        source_page = "[" + str(df_output.loc[id_correct_paragraph, "page"]) + "]"
        source = df_output.loc[id_correct_paragraph, "source"]
        paragraph_pred_rank = rank_correct_paragraph
        paragraph_pred_score = 100

    if id_correct_answer == -1:
        answer = correct_answer
        kpi_pred_rank = -1
        kpi_pred_score = -100

    else:
        answer = df_output.loc[id_correct_paragraph, "answer"]
        kpi_pred_rank = rank_correct_answer
        kpi_pred_score = df_output.loc[df_output.index == id_correct_answer, "score"].values[0]

    try:
        max_num = np.max(df_out["number"].values)
    except ValueError:
        max_num = 1

    new_data = [
        max_num + 1,
        company,
        df_output_check["pdf_name"].values[0],
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
        kpi_pred_score,
    ]
    df_series = pd.Series(new_data, index=df_temp.columns)
    df_temp = df_temp.append(df_series, ignore_index=True)
    df_temp = df_temp.set_index([pd.Index([np.max(df_out.index) + 1])])
    df_out = df_out.append(df_temp)
    df_out.tail(1)
    kpi_output.clear_output()
    val = select_kpi.value
    index = kpi_of_interest.index(val)
    select_kpi.value = kpi_of_interest[index + 1]


def update_pdf_selection(pdf_path, df_annotations, kpi_of_interest):
    pdf_selection = []
    outputs = glob.glob(pdf_path + "/*")
    outputs = [x.rsplit("/", 1)[1] for x in outputs]
    for output in outputs:
        df_output = pd.read_csv(output_path + "/" + output)
        pdf_name = df_output["pdf_name"].values[0]
        df_annotations_temp = df_annotations[df_annotations.source_file == pdf_name]
        kpis_contained = [x for x in df_annotations_temp["kpi_id"].values if x in kpi_of_interest]
        if set(kpis_contained) == set(kpi_of_interest):
            pdf_selection = select_options + [(f"DONE  - " + output, output)]
        else:
            pdf_selection = select_options + [
                (f"TODO ({len(set(kpis_contained))}/{len(kpi_of_interest)}) - " + output, output)
            ]
    return pdf_selection


def safe_annotations(path, df, replace=False):
    path = path + "/annotations.xlsx"
    if replace:
        df.to_excel(path)
    else:
        with pd.ExcelWriter(path, mode="a") as f:
            df.to_excel(f)


def lets_go():
    select_pdf_handler("value")
    select_kpi_handler("value")
    dropdown.observe(dropdown_kpi_eventhandler, names="value")
    w_dropdown_paragraph.observe(dropdown_paragraph_eventhandler, names="value")
    select_pdf.observe(select_pdf_handler, names="value")
    select_kpi.observe(select_kpi_handler, names="value")
    button_next_kpi.on_click(button_next_kpi_handler)
    select_kpi_handler("value")
    display(select_kpi)
    print("Possible answers for the chosen KPI:")
    display(kpi_output)

    # dl = widgets.dlink((dropdown, 'value'), (w_dropdown_paragraph, 'value'))

    display(dropdown, correct_answer_input)

    with output_paragraph:
        display(w_dropdown_paragraph)
    display(output_paragraph)
    display(output)
    display(button_next_kpi)
    display(button_output)


def select_the_report_to_analyze():
    select_pdf = widgets.Select(
        options=sorted(select_options, reverse=True),
        # rows=10,
        description="Available PDFs:",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="100%", height="150px"),
        disabled=False,
    )
    select_out = widgets.Output()

    display(wdg.select_pdf)
    display(wdg.select_out)


def select_your_kpi_of_interest():
    kpi_mapping_df = pd.read_csv(kpi_mapping_fpath)
    kpi_mapping_df["kpi_id"] = kpi_mapping_df["kpi_id"].map("{:g}".format)
    kpi_mapping_df.head(30)

    select_of_interest = widgets.Textarea(
        value=", ".join(kpi_mapping_df["kpi_id"].values),
        placeholder="0, 1, 2, 3.1, ...",
        layout=widgets.Layout(width="50%"),
        style={"description_width": "initial"},
        description="KPI of interest:",
        disabled=False,
    )

    display_df = kpi_mapping_df
    print("Insert your kpi of interest as a comma seperated list.\n")
    display(select_of_interest)
    print("\n")
    display(kpi_mapping_df.head(30))


def preload():
    outputs = glob.glob(output_path + "/*")
    outputs = [x.rsplit("/", 1)[1] for x in outputs]
    df_output = None
    select_options = []
    for output in outputs:
        df_output = pd.read_csv(output_path + "/" + output)
        pdf_name = df_output["pdf_name"].values[0]
        df_annotations_temp = df_annotations[df_annotations["source_file"] == pdf_name]
        kpis_contained = [x for x in df_annotations_temp["kpi_id"].values if x in kpi_of_interest]
        if set(kpis_contained) == set(kpi_of_interest):
            select_options = select_options + [(f"DONE  - " + output, output)]
        else:
            select_options = select_options + [
                (f"TODO ({len(set(kpis_contained))}/{len(kpi_of_interest)}) - " + output, output)
            ]

    options_kpi = [(x, x) for x in kpi_of_interest]

    df_output = pd.read_csv(output_path + "/" + output_file)
    df_output = df_output.drop(columns="Unnamed: 0")
    df_output_check = None
    index_list = df_output_check.index.values
    select_list = []
    for i, x in enumerate(index_list):
        select_list = select_list + [(i + 1, [i + 1, x])]
    select_list = select_list + [("no correct answer", [-1, -1])]


select_kpi = widgets.Dropdown(
    options=sorted(options_kpi),
    # rows=10,
    value=min(kpi_of_interest),
    description="Current KPI:",
    style={"description_width": "initial"},
    layout=widgets.Layout(width="100%"),
)

dropdown = widgets.Dropdown(
    description="Choose rank of correct kpi:",
    options=select_list,
    style={"description_width": "initial"},
    layout=widgets.Layout(width="50%"),
    value=None,
)

w_dropdown_paragraph = widgets.Dropdown(
    description="Choose rank of correct pagraph:",
    options=select_list,
    style={"description_width": "initial"},
    layout=widgets.Layout(width="50%"),
    value=None,
)


button_next_kpi = widgets.Button(
    value=False,
    description="Save",
    disabled=False,
    button_style="",  # 'success', 'info', 'warning', 'danger' or ''
    tooltip="Save current annotation and switch to next KPI",
    icon="check",  # (FontAwesome names without the `fa-` prefix)
)

correct_answer_input = widgets.Textarea(
    value="", placeholder="Enter your correction.", description="Correction:", layout=layout_hidden, disabled=False
)

correct_paragraph_input = widgets.Textarea(
    value="",
    placeholder="Enter your correction.",
    layout=widgets.Layout(width="60%"),
    description="Correction:",
    disabled=False,
)
