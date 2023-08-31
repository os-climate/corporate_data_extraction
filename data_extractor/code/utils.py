import argparse
import requests
import shutil
import os
import glob
import json
import yaml
import pandas as pd
from paths import path_file_running
import traceback
import pickle
import datetime
from s3_communication import S3Communication
from pathlib import Path


def set_running():
     with open(path_file_running, 'w'):
          pass


def clear_running():
     try:
          os.unlink(path_file_running)
     except Exception as e:
          pass


def check_running():
     return os.path.exists(path_file_running)


def create_directory(directory_name):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            

def link_files(source_dir, destination_dir):
    files = os.listdir(source_dir)
    for file in files:
        os.link(f"{source_dir}/{file}", f"{destination_dir}/{file}")
        

def link_extracted_files(src_ext, src_pdf, dest_ext):
    extracted_pdfs = [name[:-5] + ".pdf"  for name in os.listdir(src_ext)]
    for pdf in os.listdir(src_pdf):
        if pdf in extracted_pdfs:
            json_name = pdf[:-4] + ".json"
            # construct the src path and file name
            src_path_file_name = os.path.join(src_ext, json_name)
            # construct the dest path and file name
            dest_path_file_name = os.path.join(dest_ext, json_name)
            # test if the dest file exists, if false, do the copy, or else abort the copy operation.
            if not os.path.exists(dest_path_file_name):
                shutil.copyfile(src_path_file_name, dest_path_file_name)
    return True