import re
import shutil
import os

from scripts import editVerilog

def base_transitions(number_gates) -> list:
    result = []
    
    for i in range(number_gates):
        temp = ["X1"] * number_gates
        temp[-(i + 1)] = "X2"   
        result.append(temp)

    return result
    
class Make_verilogs:

    def __init__(self, comb: list,  verilog_name: str, verilog_templet: str, dir_to_save):
        self.comb = comb
        self.verilog_name = verilog_name
        self.verilog_templet = verilog_templet
        self.dir_to_save = dir_to_save

    def copy_and_rename(self):
        dest_path = os.path.join(self.dir_to_save, self.verilog_name)
        shutil.copy(self.verilog_templet, dest_path)

    def apply_combination(self):
        dest_path = os.path.join(self.dir_to_save, self.verilog_name)
        editVerilog.apply_combination(dest_path, self.comb, self.dir_to_save)