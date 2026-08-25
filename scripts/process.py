import threading
import numpy as np

from scripts import combinations, singleSTA, extData, utils, makeCSV, capacitance


class CellProcessor:
    
    def __init__(
        self,
        design,
        verilogs_inputs,
        out_dir,
        tcl_timing,
        netlist_module,
        netlist_inputs,
        netlist_outputs,
        features_dict,
        logic_types,
        area,
        arrival_starter,
        total_starter_area,
        csv_path,
        json_capacitance,
        map_fanouts,
    ):
        self.design = design
        self.verilogs_inputs = verilogs_inputs
        self.out_dir = out_dir
        self.tcl_timing = tcl_timing
        self.netlist_module = netlist_module
        self.netlist_inputs = netlist_inputs
        self.netlist_outputs = netlist_outputs
        self.features_dict = features_dict
        self.logic_types = logic_types
        self.area = area
        self.arrival_starter = arrival_starter
        self.total_starter_area = total_starter_area
        self.csv_path = csv_path
        self.json_capacitance = json_capacitance
        self.map_fanouts = map_fanouts

        self.cap = capacitance.Cells_cap(self.json_capacitance)

        self.csv_lock = threading.Lock()

    def create_files(self, comb, sized_cell):
        verilog_save_name = f"{sized_cell}{self.design}"

        make_verilog = combinations.Make_verilogs(
            comb,
            f"{verilog_save_name}.v",
            f"{self.verilogs_inputs}/{self.design}.v",
            f"{self.out_dir}/maped_verilogs"
        )
        make_verilog.copy_and_rename()
        make_verilog.apply_combination()

        tcl_path = f"{self.out_dir}/tcl_scripts/1{sized_cell}{self.design}.tcl"
        utils.copy_and_rename(self.tcl_timing, tcl_path)

        return tcl_path

    def capacitance_in(self, dim_cell_type):
        return self.cap.imput_capacitance(f"{dim_cell_type}_X2")

    def capacitance_out(self, dim_cell_type):
        return self.cap.out_capacitance(f"{dim_cell_type}_X2")
    
    def capacitance_load(self, sized_cell):
        loaded_keys = self.map_fanouts.get(sized_cell, set())
        conected_cells = []
        for lk in loaded_keys:
            if lk in self.features_dict.nets_and_path:
                logic_type = self.features_dict.nets_and_path[lk]["LOGIC-TYPE"]
                conected_cells.append(f"{logic_type}_X1")
        return self.cap.loaded_capacitances(conected_cells)

    def run_sta(self, tcl_path, sized_cell):
        singleSTA.run_single(
            tcl_path,
            f"{sized_cell}{self.design}.v",
            f"{self.out_dir}/maped_verilogs",
            f"{self.out_dir}/sta_out",
            self.netlist_module,
            self.netlist_inputs,
            self.netlist_outputs
        )

    def read_and_process(self, comb, sized_cell):

        cell_data = self.features_dict.nets_and_path[sized_cell]
        dim_cell_type = cell_data["LOGIC-TYPE"]
        sta_output = f"{self.out_dir}/sta_out/{sized_cell}{self.design}.txt"

        read_sta_data = extData.Read_timing(sta_output)
        arrivals = read_sta_data.get_arrival_times()
        arrivals_list = np.array(list(arrivals.values()))
        mean_arrival = utils.mean(arrivals_list)
        arrival_dif = self.arrival_starter - mean_arrival
        power = read_sta_data.get_power()

        new_comb_with_types = utils.merge_size_id(self.logic_types, comb)
        total_new_area = self.area.return_total_area(new_comb_with_types)
        cost_area = self.area.cost(total_new_area, self.total_starter_area)

        data_row = [
            self.design,
            sized_cell,
            dim_cell_type,
            cell_data["PATH-OCURENCE"],
            cell_data["PATHS-OCURENCE"],
            cell_data["FA-IN"],
            cell_data["FA-OUT"],
            cell_data["LOGIC-LEVEL"],
            cell_data["DEEP"],
            cell_data["LOADED-CELLS"],
            self.capacitance_in(dim_cell_type),
            self.capacitance_out(dim_cell_type),
            self.capacitance_load(sized_cell),
            arrival_dif,
            self.area.search_area(f"{dim_cell_type}_X2"),
            cost_area,
            power
        ]

        return data_row

    def process_cell(self, comb, sized_cell):
        
        tcl_path = self.create_files(comb, sized_cell)
        self.run_sta(tcl_path, sized_cell)
        data_row = self.read_and_process(comb, sized_cell)

        
        with self.csv_lock:
            csv_editor = makeCSV.Edit_csv(self.csv_path, data_row)
            csv_editor.insert_csv_data()

        return sized_cell