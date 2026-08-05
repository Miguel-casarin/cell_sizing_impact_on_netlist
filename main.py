import numpy as np 
import json
import time 
import sys
import os


from scripts import combinations, readV, getFeatures, dict, singleSTA, utils, extData, dir, getArea

design = "debug"
verilogs_inputs = "./verilogs"
out_dir = "./out"
lib_dir = "./library"
lib = "Nangate45_typ.lib"
tcl_timing = "timing.tcl"
tcl_starter = "timingStarter.tcl"




try:
    design_io = readV.Get_IO(f"{design}.v", verilogs_inputs)
    netlist_module = design_io.verilog_module()
    netlist_inputs = design_io.get_inputs()
    netlist_outputs = design_io.get_outputs()
except Exception as error:
    print(f"ERROR TO GET NETLIST IO:\n{error}")

try:
    design_info = readV.Gates_info(f"{design}.v", verilogs_inputs)
    cells_id = design_info.get_cells_ids()
    logic_types = design_info.logic_cells_type()
    print(f"CELLS:\n{cells_id}\nLOGIC TYPES\n{logic_types}")
except Exception as error:
    print(f"ERROR TO GET GATES INFO:\n{error}")

try:
    features_dict = dict.Manipulet_dict()
    features_dict.fild_dictionary(cells_id, logic_types)
except Exception as error:
    print(f"ERROR TO FILD DICT:\n{error}")

if len(features_dict.nets_and_path) == 0:
    print(f"Unfilled dictionary")
    sys.exit(1)

else:
    try:
        extactor_features = getFeatures.Circuits_features(f"{design}.v", verilogs_inputs, lib, lib_dir, features_dict)

        extactor_features.compute_logic_levels()
        extactor_features.comput_deep()
        extactor_features.fan_in()
        extactor_features.fan_out()
        extactor_features.loaded_cells()

    except Exception as error:
        print(f"ERROR TO LOAD FEATURES CIRCUIT TO DICT:\n{error}")

TOTAL_GATES = len(cells_id)
baseline_comb = ["X1"] * TOTAL_GATES        
transitions = combinations.base_transitions(TOTAL_GATES)

# Baseline
utils.copy_and_rename(tcl_starter, f"{out_dir}/tcl_scripts/{design}.tcl")

singleSTA.run_single(
            f"{out_dir}/tcl_scripts/{design}.tcl", 
            f"{design}.v",
            verilogs_inputs,
            f"{out_dir}/sta_out", 
            netlist_module, 
            netlist_inputs, 
            netlist_outputs
                    )

try:
    design_starter = dir.search_file(f"{design}.txt", f"{out_dir}/sta_out")
    sta_data_sized = extData.Read_timing(design_starter)
except Exception as error:
    print(f"ERROR TO READ STA OUTPUT FROM BASE LINE DESIGN:\n{error}")

try:
    arrivals_start = sta_data_sized.get_arrival_times()
    arrivals_start_sized = np.array(list(arrivals_start.values()))

    arrival_starter = utils.mean(arrivals_start_sized)
    power_stater = sta_data_sized.get_power()
except Exception as error:
    print(f"ERROR TO GET POWER AND ARRIVAL FROM NO MAPED DESIGN:\n{error}")

# Pega a ocorencia por caminho crítico usando o base line
dict_ocurence = {}
dict_paths = {}

try: 
    dict_ocurence = sta_data_sized.count_ocurence_path()
    dict_paths = sta_data_sized.ocurence_by_paths()

    # Preenche as ocorrências no dicionário principal
    utils.merge_dicts(features_dict.nets_and_path, "PATH-OCURENCE", dict_ocurence)
    utils.merge_dicts(features_dict.nets_and_path, "PATHS-OCURENCE", dict_paths)
except Exception as error:
    print(f"ERROR TO GET PATHS:\n{error}")

try:
    area = getArea.Get_Area(f"{lib_dir}/areas.json")
    initial_comb = utils.merge_size_id(logic_types, baseline_comb)
    initial_area = area.return_total_area(initial_comb)
    total_starter_area = initial_area
except Exception as errror:
    print(f"ERROR TO GET INITIAL AREA:\n{errror}")

for i in range(len(transitions)):
    
    comb = transitions[i]
    sized_cell = cells_id[i]
    verilog_save_name = f"{sized_cell}{design}"

    make_verilog = combinations.Make_verilogs(comb, f"{verilog_save_name}.v", f"{verilogs_inputs}/{design}.v", f"{out_dir}/maped_verilogs")

    make_verilog.copy_and_rename()
    make_verilog.apply_combination()

    utils.copy_and_rename(tcl_timing, f"{out_dir}/tcl_scripts/1{design}.tcl")

    singleSTA.run_single(
        f"{out_dir}/tcl_scripts/1{design}.tcl",
        f"{sized_cell}{design}.v",
        f"{out_dir}/maped_verilogs",
        f"{out_dir}/sta_out", 
        netlist_module, 
        netlist_inputs, 
        netlist_outputs
    )

# Processa o impacto das combinações e insere na tabela

 