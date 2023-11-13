"""
Authors: Dr. David Besslich and Maximilian Riefer

#13 Project: INCEpTION to Pandas
This function is used for the re-collection of marked answers out of an INCEpTION export.
"""
import logging
import time
import json
import sys
import traceback
from datetime import datetime
import pandas as pd
import glob
import os
import shutil
from cassis import *

sys.dont_write_bytecode = True

# Load settings data
with open("settings.json", "r", encoding="utf-8", errors="ignore") as settings_file:
    settings = json.load(settings_file)
    settings_file.close()


def select_covering(cas, type_name, covered_annotation, overlap):
    """Returns a list of annotations that cover the given annotation.
    Return all annotations that are covering. This can be potentially be slow.
    Depending on the choice it only returns annotations that are fully covering or also overlapping annotations.
    Args:
        cas: cassis class element
        type_name: The type name of the annotations to be returned
        covered_annotation: The name of the annotation which is covered
        overlap: Boolean if annotation are allowed to overlap multiple annotations
        Returns:
            A list of covering annotations
    """
    c_begin = covered_annotation.begin
    c_end = covered_annotation.end

    # We iterate over all annotations and check whether the provided annotation
    # is covered in the current annotation
    if overlap:
        annotations_list = []
        for annotation in cas._get_feature_structures(type_name):
            if (
                (annotation.begin <= c_begin <= annotation.end)
                or (annotation.begin <= c_end <= annotation.end)
                or (c_end >= annotation.end and c_begin <= annotation.begin)
            ):
                annotations_list.append(annotation)
        return annotations_list
    else:
        for annotation in cas._get_feature_structures(type_name):
            if c_begin >= annotation.begin and c_end <= annotation.end:
                return annotation


def specify_logger(logger):
    """
    This function create a logger object.
    :param logger: plain logger object
    :return: specified logger object
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y%m%d %H:%M:%S")
    logger_dir = settings["LogFilePath"]
    initial_time = datetime.now().strftime("%Y%m%d%H%M%S")
    fh = logging.FileHandler(logger_dir + "/" + settings["ProjectName"] + "_" + initial_time + ".log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(handler)
    print(
        "Logger information are stored in " + logger_dir + "/" + settings["ProjectName"] + "_" + initial_time + ".log"
    )
    return logger


def get_uima_cas_xmi_output(logger):
    """This file extracts from the UIMA CAS XMI type via the dkpro-cassis package
    the annotated answers and saves it into an excel sheet.

    :param logger: logging class element
    :return: None
    """
    tic = time.time()
    xmi_name = glob.glob(settings["InputPath"] + "/*.xmi")[0]
    xml_name = glob.glob(settings["InputPath"] + "/*.xml")[0]

    with open(xml_name, "rb") as f:
        typesystem = load_typesystem(f)
        f.close()

    with open(xmi_name, "rb") as f:
        cas = load_cas_from_xmi(f, typesystem=typesystem)
        f.close()

    logger.info("UIMA file loaded")

    df_answers = pd.DataFrame(
        columns=[
            "KPI",
            "ANSWER",
            "TYPE",
            "ANSWER_X",
            "ANSWER_Y",
            "PAGE",
            "PAGE_WIDTH",
            "PAGE_HEIGHT",
            "PAGE_ORIENTATION",
            "COV_SENTENCES",
        ]
    )

    for page in cas.select("org.dkpro.core.api.pdf.type.PdfPage"):
        for answer in cas.select_covered("webanno.custom.KPIAnswer", page):
            logger.info("---------------------------------------------------")
            logger.info(f'Extracting information of kpi answer "{answer.get_covered_text()}".')

            sentence_list_temp = select_covering(
                cas, "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence", answer, True
            )

            chunk_list_temp = select_covering(cas, "org.dkpro.core.api.pdf.type.PdfChunk", answer, True)
            # Find the first chunk as chunks might be mixed in order
            min_idx = 0
            for idx in range(len(chunk_list_temp)):
                if idx > 0:
                    if chunk_list_temp[0].begin < chunk_list_temp[min_idx].begin:
                        min_idx = idx
            pdf_chunk = chunk_list_temp[min_idx]
            del chunk_list_temp

            # Find now the correct position inside of the chunk to get the correct x-coordinate of the annotation
            dist_to_answer_begin = answer.begin - pdf_chunk.begin
            sum_temp = 0
            j = 0
            for j in range(len(pdf_chunk.c.elements)):
                if sum_temp >= dist_to_answer_begin:
                    break
                else:
                    sum_temp += pdf_chunk.c.elements[j]
            answer_x = pdf_chunk.g.elements[j]

            # Collect all information we want to store
            for kpi in answer.KPI.elements:
                df_answers.loc[len(df_answers)] = [
                    kpi,
                    answer.get_covered_text(),
                    "KPIAnswer",
                    answer_x,
                    pdf_chunk.y,
                    int(page.pageNumber),
                    int(page.width),
                    int(page.height),
                    int(pdf_chunk.d),
                    " ".join([x.get_covered_text() for x in sentence_list_temp]),
                ]
    if len(df_answers) > 0:
        df_answers["PDF_NAME"] = cas.select("de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData")[0][
            "documentTitle"
        ]

    logger.info("---------------------------------------------------")
    logger.info("All information have been extracted.")
    df_answers.to_excel(
        settings["OutputPath"]
        + "/"
        + settings["InputPath"].split("/")[-1]
        + "_uima_extraction_"
        + datetime.now().strftime("%Y%m%d%H%M%S")
        + ".xlsx"
    )
    toc = time.time()
    logger.info(f"Answers have been saved to excel and it took {toc - tic} seconds.")


def main(logger=logging.getLogger()):
    # FileHandler for output in logfile
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger = specify_logger(logger)

    logger.info("---------------- SETTINGS DATA ----------------")
    for key in settings:
        logger.info(str(key) + ": " + str(settings[key]))
    logger.info("------------------------------------------------")

    try:
        input_path = settings["InputPath"]
        output_path = settings["OutputPath"]
        for subfolder in [x.split("\\")[-1] for x in glob.glob(input_path + "/*") if x[-4:] != "json"]:
            settings["InputPath"] = input_path + "/" + subfolder
            output_folder = output_path + "/" + subfolder
            if not os.path.isdir(output_folder):
                os.umask(0)
                os.mkdir(output_folder, mode=0o777)
            else:
                files = os.listdir(output_folder)
                for old_file in files:
                    try:
                        os.remove(output_folder + "/" + old_file)
                    except Exception:
                        pass
            settings["OutputPath"] = output_folder

            logger.info(f'Start of UIMA file transformation for files in subfolder "' + subfolder + '".')
            get_uima_cas_xmi_output(logger)
            logger.info(
                f'UIMA file transformation for files in subfolder "' + subfolder + '" successfully made.'
                " Input files "
                "and output file are stored in the folder " + output_folder
            )
            for file in glob.glob(settings["InputPath"] + "/*"):
                shutil.copyfile(file, file.replace(settings["InputPath"], settings["OutputPath"]))

            shutil.rmtree(settings["InputPath"])

            settings["InputPath"] = input_path
            settings["OutputPath"] = output_path
    except Exception as e:
        logger.error("---ERROR---" * 10)
        logger.error(repr(e))
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
