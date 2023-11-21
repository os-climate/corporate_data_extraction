import argparse
import os, glob
import json
import csv
from sqlalchemy import engine, table, column, types


from inspect import getsourcefile
import os.path as path, sys

current_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, current_dir[: current_dir.rfind(path.sep)])
import config_path

sys.path.pop(0)


def connect_to_db(dialect, sql_driver, host, port, user, password):
    engine_path = (
        dialect + "+" + sql_driver + "://" + user + ":" + password + "@" + host + ":" + str(port)
    )  # + '/?service_name=' + SERVICE
    eng = engine.create_engine(engine_path)
    connection = eng.connect()
    return connection


def insert_csv(connection, csv_filename, run_id):
    def db_numeric(s):
        if s == "" or s is None:
            return None
        return float(s)

    nlp_raw_output = table(
        "NLP_RAW_OUTPUT",
        column("METHOD"),
        column("PDF_NAME"),
        column("KPI_ID", types.Numeric),
        column("KPI_NAME"),
        column("KPI_DESC"),
        column("ANSWER_RAW"),
        column("ANSWER"),
        column("PAGE", types.Numeric),
        column("PARAGRAPH"),
        column("POS_X", types.Numeric),
        column("POS_Y", types.Numeric),
        column("KPI_SOURCE"),
        column("SCORE", types.Numeric),
        column("NO_ANS_SCORE", types.Numeric),
        column("SCORE_PLUS_BOOST", types.Numeric),
        column("KPI_YEAR", types.Numeric),
        column("UNIT_RAW"),
        column("UNIT"),
        column("INS_RUN_ID", types.Numeric),
    )
    rows = []
    pdf_names = []
    try:
        with open(csv_filename, "r") as f:
            csv_file = csv.DictReader(f)
            for row in csv_file:
                d = dict(row)
                rows.append(
                    {
                        "METHOD": d["METHOD"],
                        "METHOD": d["METHOD"],
                        "PDF_NAME": d["PDF_NAME"],
                        "KPI_ID": db_numeric(d["KPI_ID"]),
                        "KPI_NAME": d["KPI_NAME"],
                        "KPI_DESC": d["KPI_DESC"],
                        "ANSWER_RAW": d["ANSWER_RAW"],
                        "ANSWER": d["ANSWER"],
                        "PAGE": db_numeric(d["PAGE"]),
                        "PARAGRAPH": d["PARAGRAPH"],
                        "POS_X": db_numeric(d["POS_X"]),
                        "POS_Y": db_numeric(d["POS_Y"]),
                        "KPI_SOURCE": d["KPI_SOURCE"],
                        "SCORE": db_numeric(d["SCORE"]),
                        "NO_ANS_SCORE": db_numeric(d["NO_ANS_SCORE"]),
                        "SCORE_PLUS_BOOST": db_numeric(d["SCORE_PLUS_BOOST"]),
                        "KPI_YEAR": db_numeric(d["KPI_YEAR"]),
                        "UNIT_RAW": d["UNIT_RAW"],
                        "UNIT": d["UNIT"],
                        "INS_RUN_ID": run_id,
                    }
                )
                pdf_names.append(d["PDF_NAME"])

        pdf_names = list(set(pdf_names))

        # Delete exiting entries
        for pdf_name in pdf_names:
            dele = nlp_raw_output.delete().where(nlp_raw_output.c.PDF_NAME == pdf_name)
            connection.execute(dele)

        # Insert new entries
        for row in rows:
            # print(row)
            ins = nlp_raw_output.insert().values(row)
            connection.execute(ins)
            pass
    except Exception as e:
        print("Failed to insert " + csv_filename + ". Reason: " + str(e))


def run_command(connection, run_id, cmd):
    exec_cmd = cmd.replace(":RUN_ID", str(run_id))
    connection.execute(exec_cmd)


def main():
    parser = argparse.ArgumentParser(description="End-to-end inference")

    # Add the arguments
    parser.add_argument("--project_name", type=str, default=None, help="Name of the Project")

    parser.add_argument("--run_id", type=int, default=None, help="RUN_ID Filter")

    args = parser.parse_args()
    project_name = args.project_name
    run_id = args.run_id

    if project_name is None:
        project_name = input("What is the project name? ")
    if project_name is None or project_name == "":
        print("project name must not be empty")
        return

    project_data_dir = config_path.DATA_DIR + r"/" + project_name

    # Opening JSON file
    f = open(project_data_dir + r"/settings.json")
    project_settings = json.load(f)
    f.close()

    enable_db_export = project_settings["enable_db_export"]

    if not enable_db_export:
        print("Database export is not enabled for this project.")

    db_dialect = project_settings["db_dialect"]
    db_sql_driver = project_settings["db_sql_driver"]
    db_host = project_settings["db_host"]
    db_port = project_settings["db_port"]
    db_user = project_settings["db_user"]
    db_password = project_settings["db_password"]
    db_post_command = project_settings["db_post_command"]

    print("Connecting to database " + db_host + " as " + db_user + " using password (hidden) . . . ")

    connection = connect_to_db(db_dialect, db_sql_driver, db_host, db_port, db_user, db_password)

    print("Connected. Inserting new CSV files from output . . . ")

    csv_path = project_data_dir + r"/output/" + (str(run_id) + "_" if run_id is not None else "") + "*.csv"

    for f in glob.glob(csv_path):
        print("----> " + f)
        insert_csv(connection, f, run_id)

    if db_post_command is not None and db_post_command != "":
        print("Executing post command for RUN_ID = " + str(run_id) + " . . .")
        run_command(connection, run_id, db_post_command)

    print("Closing database connection . . . ")
    connection.close()

    print("Export done.")


if __name__ == "__main__":
    main()
