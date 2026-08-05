import re

class Edit_tcl:
    def __init__(self, tcl_file, design, link_device, number_paths,  inputs_list, outputs_list):
        self.tcl_file = tcl_file
        self.design = design # Nome do arquivo
        self.link_device = link_device # Modulo do verilog
        self.number_paths = number_paths # Quantidade de caminhps criticos 
        self.inputs_list = inputs_list
        self.outputs_list = outputs_list

    def ed_device(self):
        new_verilog = f"read_verilog {self.design}"

        with open(self.tcl_file, "r") as f:
            content = f.read()

        content = re.sub(
            r"read_verilog\s+\S+", new_verilog, content
        )
        
        with open(self.tcl_file, "w") as f:
            f.write(content)

    def link_design(self):
        new_link = f"link_design {self.link_device}"

        with open(self.tcl_file, "r") as f:
            content = f.read()
        
        content = re.sub(
            r"link_design\s+\S+", new_link, content
        )

        with open(self.tcl_file, "w") as f:
            f.write(content)
    
    def paths_total(self):

        with open(self.tcl_file, "r") as f:
            content = f.read()

        content = re.sub( 
            r"(report_checks[^\n]*-group_count\s+)\d+", rf"\g<1>{self.number_paths}", content
        )

        with open(self.tcl_file, "w") as f:
            f.write(content)
    
    def parse_inputs(self):
        inputs_str = " ".join(self.inputs_list)
        new_set_inputs = f"set_input_delay 0 -clock virt_clk [get_ports {{{inputs_str}}}]"

        with open(self.tcl_file, "r") as f:
            content = f.read()

        content = re.sub(
            r"set_input_delay\s+.*?\[get_ports\s+\{.*?\}\]",
            new_set_inputs,
            content,
            flags=re.DOTALL
        )

        with open(self.tcl_file, "w") as f:
            f.write(content)


    def parse_outputs(self):
        outputs_str = " ".join(self.outputs_list)
        new_set_outputs = f"set_output_delay 1 -clock virt_clk [get_ports {{{outputs_str}}}]"

        with open(self.tcl_file, "r") as f:
            content = f.read()

        content = re.sub(
            r"set_output_delay\s+.*?\[get_ports\s+\{.*?\}\]",
            new_set_outputs,
            content,
            flags=re.DOTALL
        )

        with open(self.tcl_file, "w") as f:
            f.write(content)
   

# Contabiliza o número de outputs para usar de caminhos críticos
def number_outputs(outputs_list):
    return len(outputs_list)


# debug 
tcl_file = f"t.tcl"
design = "c17.v"
link = "c17"
paths = 2
inputs_list = ["N1", "N2", "N3", "N6", "N7"]
outputs_list = ["N22", "N23"]

"""debug = Edit_tcl(
    tcl_file,
    design,
    link,
    paths,
    inputs_list,
    outputs_list
)"""

#debug.ed_device()
#debug.link_design()
#debug.paths_total()
#debug.parse_inputs()
#debug.parse_outputs()

#ou = number_outputs(outputs_list)
#print(ou)