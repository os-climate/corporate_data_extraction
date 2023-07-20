from pathlib import Path
import pandas as pd

def write_to_file(path_csv_file: Path, content: str, header: str = ''):
    """Write to a file for a given path with an optional header string"""
    with open(str(path_csv_file), 'w') as file:
        if len(header) > 0:
            file.write(f'{header}\n')
        file.write(f'{content}\n')
        
        
def create_single_xlsx_file(path_folder: Path, file_name = 'xlsx_file.xlsx') -> None:
    """Writes a single xlsx file to path_folder and creates the folder if it does not
    exist"""
    path_folder.mkdir(parents = True, exist_ok = True)
    
    # write single xlsx file
    df_current = pd.DataFrame({'Data': [10, 20, 30, 40, 50, 60]})
    path_current_file = path_folder / file_name
    df_current.to_excel(str(path_current_file), engine='openpyxl')
    
    
def create_multiple_xlsx_files(path_folder: Path) -> None:
    """Writes multiple xlsx file to path_folder and creates the folder if it does not
    exist"""
    for i in range(5):
        create_single_xlsx_file(path_folder, file_name = f'xlsx_file_{i}.xlsx')