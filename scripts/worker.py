import os
import numpy as np 
import shutil
import traceback

from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import getArea
from scripts import utils

class Worker_combinations:

    def __init__(self, circuit, circuit_to_start, temp_dir, design_module, design_inputs, design_outputs, base_tcl, drives, json_file, TOTAL_GATES, curente_stage, logic_types, features_dict, fain_gates, faout_gates):

        self.circuit = circuit
        self.circuit_to_start = circuit_to_start
        self.temp_dir = temp_dir
        self.design_module = design_module
        self.design_inputs = design_inputs
        self.design_outputs = design_outputs
        self.base_tcl = base_tcl
        self.drives = drives
        self.json_file = json_file
        self.TOTAL_GATES = TOTAL_GATES
        self.curente_stage = curente_stage
        self.fa = getArea.Get_Area(json_file)
        self.logic_types = logic_types
        self.features_dict = features_dict
        self.fain_gates = fain_gates
        self.faout_gates = faout_gates

    def get_worker_tcl(self, worker_id: int) -> str:
        worker_tcl = os.path.join(self.temp_dir, f"t_worker_{worker_id}.tcl")
        if not os.path.exists(worker_tcl):
            shutil.copy(self.base_tcl, worker_tcl)
        return worker_tcl

    def run_sta(self, comb, work_id: int):
        worker_tcl = self.get_worker_tcl(work_id)
        id_file_sized = utils.decoder_file_name(self.TOTAL_GATES, comb)
        name_to_save  = f"{id_file_sized}_{self.circuit}.v"

        setCombination.apply_combination(self.circuit_to_start, self.temp_dir, comb, name_to_save)
        singleSTA.run_single(worker_tcl, name_to_save, self.temp_dir, self.temp_dir, self.design_module, self.design_inputs, self.design_outputs)

        sta_path = dir.search_file(f"{id_file_sized}_{self.circuit}.txt", self.temp_dir)

        return extData.Read_timing(sta_path)

    def size_weight(self, comb) -> int:
        return utils.combination_weight(comb)
    
    def get_timing(self, sta_data) -> float:
        arrivals = sta_data.get_arrival_times()

        return utils.mean(np.array(list(arrivals.values())))
    
    def get_prev_drives(self) -> list:
        return utils.merge_size_id(self.drives, self.curente_stage)

    def get_comb_drives(self, comb) -> list:
        return utils.merge_size_id(self.drives, comb)

    def get_prev_area(self) -> float:
        prev_drives = self.get_prev_drives()
        return self.fa.return_total_area(prev_drives)

    def get_comb_area(self, comb) -> float:
        comb_drives = self.get_comb_drives(comb)
        return self.fa.return_total_area(comb_drives)

    def get_area_cost(self, comb) -> float:
        prev_area = self.get_prev_area()
        comb_area = self.get_comb_area(comb)
        return self.fa.cost(comb_area, prev_area)

    def get_dim_gate(self, comb) -> int:
        return utils.find_changed_index(self.curente_stage, comb)

    def fa_in(self, dim_gate: int) -> int:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
        return self.features_dict[key]["FA-IN"]

    def fa_out(self, dim_gate: int) -> int:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
        return self.features_dict[key]["FA-OUT"]

    def logic_level(self, dim_gate: int) -> int:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
        return self.features_dict[key]["LOGIC-LEVEL"]

    def deep(self, dim_gate: int) -> int:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
        return self.features_dict[key]["DEEP"]

    def size_dim(self, comb: list, dim_gate: int) -> int:
        return utils.return_gate_size(comb, dim_gate)

    # conta a ocorrencia por caminho crítico
    # conta a ocorrencia por caminho crítico
    def count_path_occurrence(self, dim_gate: int) -> int:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
            
            # Se a chave não existir no dicionário da porta ou for None, adicionamos o valor 0 a ela
        if "PATH-OCURENCE" not in self.features_dict[key] or self.features_dict[key]["PATH-OCURENCE"] is None:
            self.features_dict[key]["PATH-OCURENCE"] = 0
                
        return self.features_dict[key]["PATH-OCURENCE"]

    def paths_occurrence(self, dim_gate: int) -> int:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
                    
        # Se a chave não existir no dicionário da porta ou for None, adicionamos o valor 0 a ela
        if "PATHS-OCURENCE" not in self.features_dict[key] or self.features_dict[key]["PATHS-OCURENCE"] is None:
            self.features_dict[key]["PATHS-OCURENCE"] = 0
                
        return self.features_dict[key]["PATHS-OCURENCE"]

    def fain_ocupation(self, comb, dim_gate: int, fain_ocupation_dict: dict):

        TOTAL_X2 = 0
        TOTAL_X4 = 0
        TOTAL_X8 = 0
        TOTAL_X16 = 0
        TOTAL_X32 = 0

        keys_list = list(self.features_dict.keys())
        index = utils.return_dict_key(keys_list, dim_gate)
        
        fain_list = fain_ocupation_dict.get(index, [])
        if fain_list:
            for gate in fain_list:
                gate_name = gate.get_name()
                
                if gate_name in keys_list:
                    gate_idx = keys_list.index(gate_name)
                    size_gate = comb[-(gate_idx + 1)]
                    
                    if size_gate == "X2":
                        TOTAL_X2 += 1
                    if size_gate == "X4":
                        TOTAL_X4 += 1
                    if size_gate == "X8":
                        TOTAL_X8 += 1
                    if size_gate == "X16":
                        TOTAL_X16 += 1
                    if size_gate == "X32":
                        TOTAL_X32 += 1

        return [("X2", TOTAL_X2), ("X4", TOTAL_X4), ("X8", TOTAL_X8), ("X16", TOTAL_X16), ("X32", TOTAL_X32)]

    def faout_ocupation(self, comb, dim_gate: int, faout_ocupation_dict: dict):
    
        TOTAL_X2 = 0
        TOTAL_X4 = 0
        TOTAL_X8 = 0
        TOTAL_X16 = 0
        TOTAL_X32 = 0

        keys_list = list(self.features_dict.keys())
        index = utils.return_dict_key(keys_list, dim_gate)
        
        faout_list = faout_ocupation_dict.get(index, [])
        if faout_list:
            for gate in faout_list:
                gate_name = gate.get_name()
                
                if gate_name in keys_list:
                    gate_idx = keys_list.index(gate_name)
                    size_gate = comb[-(gate_idx + 1)]
                    
                    if size_gate == "X2":
                        TOTAL_X2 += 1
                    if size_gate == "X4":
                        TOTAL_X4 += 1
                    if size_gate == "X8":
                        TOTAL_X8 += 1
                    if size_gate == "X16":
                        TOTAL_X16 += 1
                    if size_gate == "X32":
                        TOTAL_X32 += 1

        return [("X2", TOTAL_X2), ("X4", TOTAL_X4), ("X8", TOTAL_X8), ("X16", TOTAL_X16), ("X32", TOTAL_X32)]
    
    def update_stage(self, new_stage):
        self.curente_stage = new_stage

    def get_cell_area(self, comb: list, dim_gate: int) -> float:
        drive = self.size_dim(comb, dim_gate)
        size_type = utils.logict_type_drive(self.logic_types, dim_gate, drive)
        return self.fa.search_area(size_type)

    def get_logic_type(self, dim_gate: int) -> str:
        key = utils.return_dict_key(list(self.features_dict.keys()), dim_gate)
        return self.features_dict[key]["LOGIC-TYPE"]

    def process(self, comb, worker_id: int) -> dict | None:
        try:
            sta_data  = self.run_sta(comb, worker_id)
            mean_arr  = self.get_timing(sta_data)
            power     = sta_data.get_power()
            dim_gate  = self.get_dim_gate(comb)

            return {
                "comb":                comb,
                "size":                self.size_dim(comb, dim_gate),
                "size_weight":         self.size_weight(comb),
                "mean_arrivals_sized": mean_arr,
                "power":               power,
                "area_cost":           self.get_area_cost(comb),
                "dim_gate":            utils.return_dict_key(list(self.features_dict.keys()), dim_gate),
                "cell-area":           self.get_cell_area(comb, dim_gate),
                "logic_type":          self.get_logic_type(dim_gate),
                "prev_drives":         self.get_prev_drives(),
                "comb_drives":         self.get_comb_drives(comb),
                "prev_area":           self.get_prev_area(),
                "comb_area":           self.get_comb_area(comb),
                "occurrence":          self.count_path_occurrence(dim_gate),
                "occurrence_paths":    self.paths_occurrence(dim_gate),
                "fa_in":               self.fa_in(dim_gate),
                "fa_out":              self.fa_out(dim_gate),
                "logic_level":         self.logic_level(dim_gate),
                "deep":                self.deep(dim_gate),
                "fain_ocup":           self.fain_ocupation(comb, dim_gate, self.fain_gates),
                "faout_ocup":          self.faout_ocupation(comb, dim_gate, self.faout_gates)
            }
        
        except Exception as error:
            print(f"[Worker {worker_id}] ERRO em {comb}: {error}")
            # Não engolimos mais o erro aqui. Relançamos com contexto
            # (combinação + worker) e preservando o traceback original,
            # para que o loop principal capture e dê break imediatamente.
            raise RuntimeError(
                f"[Worker {worker_id}] Falha ao processar combinação {comb}: {error}\n"
                f"{traceback.format_exc()}"
            ) from error
