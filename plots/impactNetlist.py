import os 
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import extData, utils, singleSTA, dict, readV

design = "c17"
verilogs_inputs = "../verilogs"
out_dir = "../out"
lib_dir = "../library"
lib = "Nangate45_typ.lib"
tcl_timing = "timing.tcl"

try:
    design_io = readV.Get_IO(f"{design}.v", verilogs_inputs)
    netlist_module = design_io.verilog_module()
    netlist_inputs = design_io.get_inputs()
    netlist_outputs = design_io.get_outputs()
except Exception as error:
    print(f"ERROR TO GET NETLIST IO:\n{error}")

# Retorna as celulas do netlist
try:
    design_info = readV.Gates_info(f"{design}.v", verilogs_inputs)
    cells_id = design_info.get_cells_ids()
    print(f"CELLS:\n{cells_id}")
except Exception as error:
    print(f"ERROR TO GET GATES INFO:\n{error}")

# Puxa o sta para cada uma das combinações
files_list = utils.make_files_list(cells_id, design)
print(files_list)

for file in files_list:
    sized_gate = re.match(r'^_\d+_', file).group()
    print(sized_gate)
