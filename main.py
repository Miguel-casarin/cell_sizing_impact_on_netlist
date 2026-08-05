import numpy as np 
import json
import time 
import sys
import os


from scripts import combinations, readV, getFeatures, dict, singleSTA, utils

design = "debug"
verilogs_inputs = "./verilogs"
out_dir = "./out"
lib_dir = "./library"
lib = "Nangate45_typ.lib"





try:
    design_io = readV.Get_IO(f"{design}.v", verilogs_inputs)
    netlist_module = design_io.verilog_module()
    netlist_inputs = design_io.get_inputs()
    netlist_outputs = design_io.get_inputs()
except Exception as error:
    print(f"ERROR TO GET NETLIST IO:\n{error}")

try:
    design_info = readV.Gates_info(f"{design}.v", verilogs_inputs)
    cells_id = design_info.get_cells_ids()
    logic_types = design_info.logic_cells_type()
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
        
transitions = combinations.base_transitions(len(cells_id))

# Baseline
singleSTA.run_single()

base_arrivel = 0
base_power = 0
base_total_area = 0

for i in range(len(transitions)):
    
    comb = transitions[i]
    sized_cell = cells_id[i]
    verilog_save_name = f"{sized_cell}{design}"

    make_verilog = combinations.Make_verilogs(comb, f"{verilog_save_name}.v", f"{verilogs_inputs}/{design}.v", f"{out_dir}/maped_verilogs")

    make_verilog.copy_and_rename()
    make_verilog.apply_combination()
   