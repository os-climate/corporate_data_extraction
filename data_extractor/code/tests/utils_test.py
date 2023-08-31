from pathlib import Path
import pandas as pd
import typing


def project_tests_root() -> Path:
    """returns the absolute project root path

    :return: Path to the current project root
    :rtype: Path
    """
    return Path(__file__).parent.resolve()


def write_to_file(path_csv_file: Path, content: str, header: str = ''):
    """Write to a file for a given path with an optional header string

    :param path_csv_file: Path to csv file
    :type path_csv_file: Path
    :param content: Content which should be written to csv file
    :type content: str
    :param header: Header of the csv file, defaults to ''
    :type header: str, optional
    """
    with open(str(path_csv_file), 'w') as file:
        if len(header) > 0:
            file.write(f'{header}\n')
        file.write(f'{content}\n')
        
        
def create_single_xlsx_file(path_folder: Path, file_name = 'xlsx_file.xlsx') -> None:
    """Writes a single xlsx file to path_folder and creates the folder if it does not
    exist

    :param path_folder: Path to folder where the single xlsx file should be created
    :type path_folder: Path
    :param file_name: Filename of the xlsx file, defaults to 'xlsx_file.xlsx'
    :type file_name: str, optional
    """
    path_folder.mkdir(parents = True, exist_ok = True)
    
    # write single xlsx file
    df_current = pd.DataFrame({'Data': [10, 20, 30, 40, 50, 60]})
    path_current_file = path_folder / file_name
    df_current.to_excel(str(path_current_file), engine='openpyxl')
    
    
def create_multiple_xlsx_files(path_folder: Path) -> None:
    """Writes multiple xlsx file to path_folder and creates the folder if it does not
    exist

    :param path_folder: Path to folder where the single xlsx file should be created
    :type path_folder: Path
    """
    for i in range(5):
        create_single_xlsx_file(path_folder, file_name = f'xlsx_file_{i}.xlsx')

def modify_project_settings(project_settings: typing.Dict, 
                            *args: typing.Tuple[str, str, bool]) -> typing.Dict:
    """Returns are modified project settings dict based on the input args

    :param project_settings: Project settings
    :type project_settings: typing.Dict
    :return: Modified project settings
    :rtype: typing.Dict
    """
    for modifier in args:
        # check for valid args
        if len(modifier) == 3:
            key1, key2, decision = modifier
            project_settings[key1][key2] = decision
    return project_settings
