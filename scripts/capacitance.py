import najaeda
from najaeda import netlist, naja
import json
import re
import pprint

#import readV

# Para cada gate do netlist retorna os gates alimentados pelo seus faout
class Netlist_fouts:
    def __init__(self, library: str, base_verilog):
        self.library = library
        self.base_verilog = base_verilog

        netlist.reset()
        netlist.load_liberty(self.library)
        self.top = netlist.load_verilog([self.base_verilog])
        self.circuit_gates = list(self.top.get_leaf_children())

    def extract_key(self, inst_name) -> str:
            match = re.search(r'_\d+_', inst_name)
            return match.group(0) if match else None

    def direct_fanout_map(self) -> dict:
        fanout_map = {}

        for gate in self.circuit_gates:
            gate_key = self.extract_key(gate.get_name())
            if gate_key is None:
                continue
 
            loaded = set()
 
            for out_term in gate.get_output_terms():
                for bit_term in out_term.get_bits():
                    equipotential = bit_term.get_equipotential()
                    for reader in equipotential.get_leaf_readers():
                        next_inst = reader.get_instance()
 
                        # evita contar o proprio gate (ex: laco estranho/feedback)
                        if next_inst.get_name() == gate.get_name():
                            continue
 
                        next_key = self.extract_key(next_inst.get_name())
                        if next_key is not None:
                            loaded.add(next_key)
 
            fanout_map[gate_key] = loaded
 
        return fanout_map


class Cells_cap:

    def __init__(self, json_capacitance):
        self.json_capacitance = json_capacitance

    def imput_capacitance(self, cell: str) -> float:
        with open(self.json_capacitance, "r") as f:
            lib = json.load(f)

        return lib[cell]["inputs_pins"]

    def out_capacitance(self, cell) -> float:
        with open(self.json_capacitance, "r") as f:
            lib = json.load(f)

        return lib[cell]["output_pins"]

    def loaded_capacitances(self, conected_cells: list) -> float:
        total_cap = 0
        for cell in conected_cells:
            cap = self.imput_capacitance(cell)
            total_cap = total_cap + cap

        return total_cap

# design = "c432.v"   
# ds_dir = "../verilogs"
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from scripts import readV

# base_verilog = "../verilogs/debug.v"
# lib = "../library/Nangate45_typ.lib"
# json_cap = "../library/capacitance.json"
    
# cells_c = Cells_cap(json_cap)
# map = Netlist_fouts(lib, base_verilog)
# cap_dict = map.direct_fanout_map()
# pprint.pprint(cap_dict)

# # Get cells_id and logic types to map the instances
# design_info = readV.Gates_info("debug.v", "../verilogs")
# cells_id = design_info.get_cells_ids()
# logic = design_info.logic_cells_type()

# print("\n--- TEST INPUT CAPACITANCE ---")
# for key in cap_dict:
#     p = cells_id.index(key)
#     l = logic[p]
#     c = f"{l}_X1"
#     print(f"Cell {key} ({c}) INPUT = {cells_c.imput_capacitance(c)}")

# print("\n--- TEST LOADED CAPACITANCES ---")
# for key, loaded_keys in cap_dict.items():
#     p = cells_id.index(key)
#     l = logic[p]
#     c = f"{l}_X1"
    
#     # Map all loaded instance keys to their cell types
#     conected_cells = []
#     for loaded_key in loaded_keys:
#         p_loaded = cells_id.index(loaded_key)
#         l_loaded = logic[p_loaded]
#         c_loaded = f"{l_loaded}_X1"
#         conected_cells.append(c_loaded)
        
#     loaded_cap = cells_c.loaded_capacitances(conected_cells)
#     print(f"Cell {key} ({c}) is loaded by {loaded_keys} -> LOADED_CAP = {loaded_cap}")