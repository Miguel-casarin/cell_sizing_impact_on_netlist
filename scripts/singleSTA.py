import re
import subprocess
import os

from scripts import edTCL

def rename(string):
    id = re.match(r'^(.*)\.v$', string)

    if id:
        return id.group(1)
    
def open_sta(tcl_script, name_to_save: str, out_dir):
    name = f"{name_to_save}.txt"
    output_path = os.path.join(out_dir, name)

    with open(output_path, "w") as f:
        subprocess.run(
        ["sta", tcl_script],
        stdout=f,
        stderr=subprocess.STDOUT,  # STDOUT serve para mostrar os erros
        text=True
        )

def run_single(file_tcl, circuit_process, dir_circuits, dir_to_save, module_design, inputs_sinals, outputs_signals):

    
    number_paths = edTCL.number_outputs(outputs_signals)

    design_path = f"{dir_circuits}/{circuit_process}"

    script_sta = edTCL.Edit_tcl(
        file_tcl,        
        design_path,     
        module_design,   
        number_paths,    
        inputs_sinals,   
        outputs_signals  
        )
    
    script_sta.ed_device()
    script_sta.link_design()
    script_sta.paths_total()
    script_sta.parse_inputs()
    script_sta.parse_outputs()

    name_txt = rename(circuit_process)
    
    try:
        open_sta(file_tcl, name_txt, dir_to_save)
        print(f"Circuit {circuit_process} analyzes in STA")
        
    except Exception as error:
            print(f"Error to run OpenSTA: {error}")