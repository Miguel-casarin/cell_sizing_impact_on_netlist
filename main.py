import numpy as np 
import json
import time 
import sys
import os


from scripts import combinations, readV, getFeatures, dict, singleSTA, utils, extData, dir, getArea, makeCSV

coluns_list = [
    "DESIGN",
    "CELL",
    "LOGIC-TYPE",
    "PATH-OCURENCE",
    "PATHS-OCURENCE",
    "FA-IN",
    "FA-OUT",
    "LOGIC-LEVEL",
    "DEEP",
    "LOADED-CELLS",
    "DIF-ARRIVAL",
    "CELL-AREA",
    "COST-AREA",
    "POWER"
]


design = "c17"
verilogs_inputs = "./verilogs"
out_dir = "./out"
lib_dir = "./library"
lib = "Nangate45_typ.lib"
tcl_timing = "timing.tcl"
tcl_starter = "timingStarter.tcl"

start_timer = time.time()



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

# Criação do CSV antes do loop
csv_dir = "./csv"
csv_path = f"{csv_dir}/{design}.csv"
csv_table = makeCSV.Create_table(coluns_list, csv_dir, csv_path)
csv_table.make_csv()

# Processa o impacto das combinações e insere na tabela
for j in range(len(transitions)):
    sized_cell = cells_id[j]
    sta_output = f"{out_dir}/sta_out/{sized_cell}{design}.txt"

    read_sta_data = extData.Read_timing(sta_output)
    arrivals = read_sta_data.get_arrival_times()
    arrivals_list = np.array(list(arrivals.values()))
    mean_arrival = utils.mean(arrivals_list)

    # impacto do dimensionamento da celula no circuito
    arrival_dif = arrival_starter - mean_arrival

    power = read_sta_data.get_power()
    
    dim_cell_type = features_dict.nets_and_path[sized_cell]["LOGIC-TYPE"]
    dim_cell_path = features_dict.nets_and_path[sized_cell]["PATH-OCURENCE"]
    dim_cell_paths = features_dict.nets_and_path[sized_cell]["PATHS-OCURENCE"]
    fain_dim_cell = features_dict.nets_and_path[sized_cell]["FA-IN"]
    faout_dim_cell = features_dict.nets_and_path[sized_cell]["FA-OUT"]
    logic_level_dim = features_dict.nets_and_path[sized_cell]["LOGIC-LEVEL"]
    deep_dim_cell = features_dict.nets_and_path[sized_cell]["DEEP"]
    loded_cells_by_dim = features_dict.nets_and_path[sized_cell]["LOADED-CELLS"]

    cell_dim_area = area.search_area(f"{dim_cell_type}_X2")

    # 1. Pega a combinação inteira desta iteração atual (j)
    comb = transitions[j]

    # 2. Faz o merge dos tipos lógicos com os novos tamanhos gerando ex: ["AND_X1", "NOR_X2", ...]
    new_comb_with_types = utils.merge_size_id(logic_types, comb)
    
    # 3. Calcula a NOVA área TOTAL do circuito
    total_new_area = area.return_total_area(new_comb_with_types)
    
    # 4. Calcula o CUSTO como a diferença entre a Área Total Nova e a Área Total Original
    cost_area = area.cost(total_new_area, total_starter_area)

    print(f"------ {design} ------")
    print(f"------ {sized_cell} ------")
    print(f"type: {dim_cell_type}")
    print(f"fain: {fain_dim_cell}\nfaout: {faout_dim_cell}\nlogic level: {logic_level_dim}\ndeep: {deep_dim_cell}\nloded cells: {loded_cells_by_dim}")
    print(f"arrival: {mean_arrival}  -  arrival dif: {arrival_dif}")
    print(f"power: {power}")
    print(f"cell area: {cell_dim_area}\nbase area: {initial_area}\ncost area: {cost_area}")

    # Salva a linha no CSV
    data_row = [
        design,
        sized_cell,
        dim_cell_type,
        dim_cell_path,
        dim_cell_paths,
        fain_dim_cell,
        faout_dim_cell,
        logic_level_dim,
        deep_dim_cell,
        loded_cells_by_dim,
        arrival_dif,
        cell_dim_area,
        cost_area,
        power
    ]
    csv_editor = makeCSV.Edit_csv(csv_path, data_row)
    csv_editor.insert_csv_data()

end_timer = time.time()
print(f"TEMPO TOTAL {(end_timer - start_timer) / 60:.2f} min")