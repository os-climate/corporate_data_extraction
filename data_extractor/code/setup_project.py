import argparse
import os
import shutil

import config_path


def main():
    parser = argparse.ArgumentParser(description="Setup new NLP project")
    # Add the arguments
    parser.add_argument("--project_name", type=str, default=None, help="Name of the Project")
    args = parser.parse_args()
    project_name = args.project_name

    if project_name is None:
        project_name = input("What is the project name? ")

    if project_name is None or project_name == "":
        print("project name must not be empty")
        return

    os.makedirs(config_path.DATA_DIR + r"/" + project_name, exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/input", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/input/pdfs", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/input/kpi_mapping", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/input/annotations", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/input/pdfs/training", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/input/pdfs/inference", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/interim", exist_ok=True)
    os.makedirs(config_path.DATA_DIR + r"/" + project_name + r"/output", exist_ok=True)
    shutil.copy(
        config_path.DATA_DIR + r"/settings_default.yaml", config_path.DATA_DIR + r"/" + project_name + r"/settings.yaml"
    )


if __name__ == "__main__":
    main()
