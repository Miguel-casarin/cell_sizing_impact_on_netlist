import os
import csv
import numpy as np
import shutil

from scripts import Decoder
from scripts import makeCSV


# retorna uma lista dos tipos logicos com os drives stanges
def merge_size_id(drives_list: list, comb_list: list) -> list:
    merge_list = []
    try:
        for drive, comb in zip(reversed(drives_list), comb_list):
            d = f"{drive}_{comb}"
            merge_list.append(d)
    except Exception as error:
        print(f"ERROR to merge drives {error}")

    return merge_list

# Retorna a string TIPO_X(SIZE) individualmente do gate dimensionado 
def logict_type_drive(logic_types_list: list, dim_gate: int, drive_stante: int) -> str:
    logic_type = logic_types_list[dim_gate -1]
    type_sized = f"{logic_type}_X{drive_stante}"
    return type_sized

def find_changed_index(original: list, modified: list) -> int:
    for offset, (old, new) in enumerate(
        zip(reversed(original), reversed(modified))
    ):
        if old != new:
            return offset + 1
    return -1

def create_csv(coluns_to_make, csv_dir, csv_path):
    table = makeCSV.Create_table(coluns_to_make, csv_dir, csv_path)
    table.make_csv()

def is_dir_empty(path):
    return not any(os.scandir(path))

def mean(values: list) -> float:
    return np.mean(values)


def clear_temp_dir(verilog_maintain: str, sta_maintain: str, dir_to_clear: str) -> None:
    keep_files = {verilog_maintain, sta_maintain}
    extensions_to_remove = {".txt", ".v"}

    for file in os.listdir(dir_to_clear):
        file_path = os.path.join(dir_to_clear, file)

        if not os.path.isfile(file_path):
            continue

        _, extension = os.path.splitext(file)

        if file not in keep_files and extension in extensions_to_remove:
            os.remove(file_path)

def clear_directory(directory: str) -> None:
    extensions_to_delete = {
        ".txt",
        ".v",
        ".tcl",
    }

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if not os.path.isfile(file_path):
            continue

        _, extension = os.path.splitext(file)

        if extension in extensions_to_delete:
            os.remove(file_path)

def combination_weight(comb: list) -> int:
    weight = 0
    for gate in comb:
        value = int(gate[1:])
        weight += value

    return weight

def update_chosen_by_index(csv_path: str, row_index: int, chosen_value: int):
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = rows[0]
    chosen_idx = header.index("CHOSEN")

    if row_index < 1 or row_index >= len(rows):
        print(f"Índice {row_index} fora do range do CSV ({len(rows)-1} linhas).")
        return

    rows[row_index][chosen_idx] = str(chosen_value)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

def order_dict(original_dict: dict) -> dict:
    return dict(
        sorted(
            original_dict.items(),
            key=lambda item: int(item[0].strip('_'))
        )
    )

def dict_to_list(original_dict: dict) -> list:
    sorted_dict = order_dict(original_dict)
    return list(sorted_dict.values())

def return_gate_size(combination: list, dim_gate: int) -> int:
    gate = combination[-dim_gate]
    return int(gate[1:])

# recebe o valor do gate e retorna a chave do dicionario de features equivalente
def return_dict_key(dict_keys_list: list, dim_gate) -> int:
    indice = dim_gate - 1
    return dict_keys_list[indice]

def merge_dicts(dict_base: dict, field_base: str, dict_update: dict, field_update: str = None) -> None:
    for key, update_entry in dict_update.items():
        if key in dict_base:
            if field_update:
                dict_base[key][field_base] = update_entry[field_update]
            else:
                dict_base[key][field_base] = update_entry
        else:
            print(f"ERROR to merge path ocurence in base dict")

def copy_and_rename(tamplete_file: str, output_file: str) -> None:
    shutil.copy(tamplete_file, output_file)