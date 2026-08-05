from collections import deque
import os 
from najaeda import netlist, naja
import re

#netlist.reset()
#netlist.load_liberty(["Nangate45_typ.lib"])
#top = netlist.load_verilog(["c17.v"])

#def explore_design(instance):    
    #print(f"{instance.get_name()} with model: {instance.get_model_name()}")    
    #for ins in instance.get_child_instances():        
        #explore_design(ins)
        
#explore_design(top)

class Netlist_info:
    def __init__(self, verilog, verilog_path,  libray, libraey_path):
        self.verilog = verilog
        self.verilog_path = verilog_path
        self.path_v = os.path.join(self.verilog_path, self.verilog)
        
        self.libray = libray
        self.libray_path = libraey_path
        self.path_lib = os.path.join(self.libray_path, self.libray)
    
    def print_nets(self):
        netlist.reset()
        netlist.load_liberty([self.path_lib])
        top = netlist.load_verilog([self.path_v])

        for inst in top.get_child_instances():
            print(f"Instance {inst.get_name()}")
            for term in inst.get_terms():
                print(f"  Pin: {term.get_name()} ({term.get_direction()})")
                print(f"    Net: {term.get_upper_net().get_name()}")
                
    
class Circuits_features:
    def __init__(self, verilog, verilog_path,  libray, libraey_path, features_dict=None):
        self.verilog = verilog
        self.verilog_path = verilog_path
        self.path_v = os.path.join(self.verilog_path, self.verilog)
        
        self.libray = libray
        self.libray_path = libraey_path
        self.path_lib = os.path.join(self.libray_path, self.libray)

        self.features_dict = features_dict

        netlist.reset()
        netlist.load_liberty([self.path_lib])
        self.top_najaeda = netlist.load_verilog([self.path_v])

        self.universe = naja.NLUniverse.get()
        self.top = self.universe.getTopDesign()

    def extract_key(self, inst_name):
        match = re.search(r'_\d+_', inst_name)
        return match.group(0) if match else None

    def compute_logic_levels(self):
        top = self.top

        # mapeia:
        #  - inst_name -> instância
        #  - inst_name -> conjunto de nets de entrada
        instances = {}
        inst_inputs = {}

        for inst in top.getInstances():
            name = inst.getName()
            instances[name] = inst
            in_nets = set()
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Input:
                    continue
                net = term.getNet()
                if net:
                    in_nets.add(net)
            inst_inputs[name] = in_nets

        # conjunto de nets ligadas diretamente às entradas primárias (PIs)
        pi_nets = set()
        for term in top.getBitTerms():
            if term.getDirection() != naja.SNLTerm.Direction.Input:
                continue
            net = term.getNet()
            if net:
                pi_nets.add(net)

        # mapeia net -> instâncias que a dirigem (fanin)
        net_drivers = {}
        for inst in top.getInstances():
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Output:
                    continue
                net = term.getNet()
                if not net:
                    continue
                net_drivers.setdefault(net, set()).add(inst)

        levels = {}
        
        changed = True

        while changed:
            changed = False
            for inst_name, in_nets in inst_inputs.items():
                if inst_name in levels:
                    continue

                all_from_pi = True
                drivers_levels = []
                resolvable = True

                for net in in_nets:
                    if net in pi_nets:
                        continue  # entrada primária, ok

                    all_from_pi = False
                    drivers = net_drivers.get(net, set())
                    if not drivers:
                        resolvable = False
                        break

                    local_levels = []
                    for drv in drivers:
                        drv_name = drv.getName()
                        if drv_name not in levels:
                            resolvable = False
                            break
                        local_levels.append(levels[drv_name])

                    if not resolvable:
                        break

                    drivers_levels.append(max(local_levels))

                if not resolvable:
                    continue

                if all_from_pi:
                    levels[inst_name] = 1
                else:
                    levels[inst_name] = max(drivers_levels) + 1

                changed = True

        for inst_name, level in levels.items():
            key = self.extract_key(inst_name)
            if key is not None and self.features_dict and (key in self.features_dict.nets_and_path):
                self.features_dict.ad_logic_level(key, level)

    def comput_deep(self):
        top = self.top

        # mapeia instâncias e suas nets de saída
        inst_outputs = {}
        for inst in top.getInstances():
            name = inst.getName()
            out_nets = set()
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Output:
                    continue
                net = term.getNet()
                if net:
                    out_nets.add(net)
            inst_outputs[name] = out_nets

        # nets ligadas diretamente às saídas primárias (POs)
        po_nets = set()
        for term in top.getBitTerms():
            if term.getDirection() != naja.SNLTerm.Direction.Output:
                continue
            net = term.getNet()
            if net:
                po_nets.add(net)

        # mapeia net -> instâncias que usam essa net como ENTRADA (fanout)
        net_users = {}
        for inst in top.getInstances():
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Input:
                    continue
                net = term.getNet()
                if not net:
                    continue
                net_users.setdefault(net, set()).add(inst)

        deep = {}

        # 1) gates diretamente ligados a uma saída primária: deep = 1
        for inst_name, out_nets in inst_outputs.items():
            if any(net in po_nets for net in out_nets):
                deep[inst_name] = 1

        # 2) propaga para trás: deep = 1 + max(deep dos fanouts)
        changed = True
        while changed:
            changed = False
            for inst_name, out_nets in inst_outputs.items():
                if inst_name in deep:
                    continue

                resolvable = True
                fanout_deeps = []

                for net in out_nets:
                    users = net_users.get(net, set())
                    if not users:
                        # net que não leva a lugar nenhum não contribui
                        continue

                    local = []
                    for u in users:
                        u_name = u.getName()
                        if u_name not in deep:
                            resolvable = False
                            break
                        local.append(deep[u_name])

                    if not resolvable:
                        break

                    if local:
                        fanout_deeps.append(max(local))

                if not resolvable or not fanout_deeps:
                    continue

                deep[inst_name] = max(fanout_deeps) + 1
                changed = True

        for inst_name, dp in deep.items():
            key = self.extract_key(inst_name)
            if key is not None and self.features_dict and (key in self.features_dict.nets_and_path):
                self.features_dict.ad_deep(key, dp)

    def fan_in(self):
        top = self.top

        # para cada instância, conta quantos pinos de entrada ela possui
        for inst in top.getInstances():
            name = inst.getName()
            count = 0
            for term in inst.getInstTerms():
                if term.getDirection() == naja.SNLTerm.Direction.Input:
                    count += 1
            
            key = self.extract_key(name)
            if key is not None and self.features_dict and (key in self.features_dict.nets_and_path):
                self.features_dict.ad_fanin(key, count)

    def fan_out(self):
        top = self.top

        # mapeia, para cada instância, quais nets ela dirige (saídas)
        inst_outputs = {}
        for inst in top.getInstances():
            name = inst.getName()
            out_nets = set()
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Output:
                    continue
                net = term.getNet()
                if net:
                    out_nets.add(net)
            inst_outputs[name] = out_nets

        # mapeia net -> instâncias que usam essa net como entrada (fanout físico)
        net_users = {}
        for inst in top.getInstances():
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Input:
                    continue
                net = term.getNet()
                if not net:
                    continue
                net_users.setdefault(net, set()).add(inst.getName())

        # fan-out em número de gates: quantos gates recebem essa saída
        for inst_name, out_nets in inst_outputs.items():
            destinations = set()
            for net in out_nets:
                for user_name in net_users.get(net, set()):
                    if user_name != inst_name:  # evita contar auto-loop estranho
                        destinations.add(user_name)
            
            key = self.extract_key(inst_name)
            if key is not None and self.features_dict and (key in self.features_dict.nets_and_path):
                self.features_dict.ad_fanout(key, len(destinations))
    
    # Retorna a quantidade de células subsequentes (cone de fanout) que cada gate carrega no output
    def loaded_cells(self):
        top = self.top_najaeda

        for gate in top.get_leaf_children():
            visited = set()
            queue = deque([gate])
            total_loaded = 0

            while queue:
                inst = queue.popleft()

                for out_term in inst.get_output_terms():
                    for bit_term in out_term.get_bits():
                        equipotential = bit_term.get_equipotential()
                        for reader in equipotential.get_leaf_readers():
                            next_inst = reader.get_instance()
                            if next_inst not in visited:
                                visited.add(next_inst)
                                queue.append(next_inst)
                                total_loaded += 1
            
            key = self.extract_key(gate.get_name())
            if key is not None and self.features_dict and (key in self.features_dict.nets_and_path):
                self.features_dict.ad_loaded(key, total_loaded)
class sized_ocupation:
    def __init__(self, verilog, library):
        self.verilog = verilog
        self.library = library

        netlist.reset()
        netlist.load_liberty([self.library])
        self.top_najaeda = netlist.load_verilog([self.verilog])

        self.universe = naja.NLUniverse.get()
        self.top = self.universe.getTopDesign()

        # Eu não estou exluindo assigns nem black box's, issso pode dar problema no futuro se o verilog de entrada não estiver limpo

        self.circuit_gates = list(self.top_najaeda.get_leaf_children())

    def faout_sized_ocupation(self) -> dict:

        faout_ocupation = {}
        for gate in self.circuit_gates:
            gate_name = gate.get_name()
            visited = set()
            queue = deque([gate])

            faout_ocupation[gate_name] = {}
            total_x2 = 0
            total_x4 = 0
            total_x8 = 0
            total_x16 = 0
            total_x32 = 0

            while queue:
                inst = queue.popleft()

                for out_term in inst.get_output_terms():
                    for bit_term in out_term.get_bits():
                        equipotential = bit_term.get_equipotential()
                        for reader in equipotential.get_leaf_readers():
                            next_inst = reader.get_instance()

                            key = next_inst.get_name()  # nome da instância, ex: _123_
                            if key not in visited:
                                visited.add(key)
                                queue.append(next_inst)
                                
                                model_name = next_inst.get_model_name() # nome da célula, ex: NAND2_X4
                                match = re.search(r'_X(\d+)$', model_name)

                                if match:
                                    match_str = match.group(1)
                                    if match_str == "2":
                                        total_x2 +=1
                                    elif match_str == "4":
                                        total_x4 +=1
                                    elif match_str == "8":
                                        total_x8 +=1
                                    elif match_str == "16":
                                        total_x16 +=1
                                    elif match_str == "32":
                                        total_x32 +=1

            faout_ocupation[gate_name]["TOTAL-X2"] = total_x2
            faout_ocupation[gate_name]["TOTAL-X4"] = total_x4
            faout_ocupation[gate_name]["TOTAL-X8"] = total_x8
            faout_ocupation[gate_name]["TOTAL-X16"] = total_x16
            faout_ocupation[gate_name]["TOTAL-X32"] = total_x32
            
        return faout_ocupation
    
    def fain_sized_ocupation(self) -> dict:

        fain_ocupation = {}
        for gate in self.circuit_gates:
            gate_name = gate.get_name()
            visited = set()
            queue = deque([gate])

            fain_ocupation[gate_name] = {}
            total_x2 = 0
            total_x4 = 0
            total_x8 = 0
            total_x16 = 0
            total_x32 = 0

            while queue:
                inst = queue.popleft()

                for out_term in inst.get_input_terms():
                    for bit_term in out_term.get_bits():
                        equipotential = bit_term.get_equipotential()
                        for reader in equipotential.get_leaf_drivers():
                            next_inst = reader.get_instance()

                            key = next_inst.get_name()  # nome da instância, ex: _123_
                            if key not in visited:
                                visited.add(key)
                                queue.append(next_inst)
                                
                                model_name = next_inst.get_model_name() # nome da célula, ex: NAND2_X4
                                match = re.search(r'_X(\d+)$', model_name)

                                if match:
                                    match_str = match.group(1)
                                    if match_str == "2":
                                        total_x2 +=1
                                    elif match_str == "4":
                                        total_x4 +=1
                                    elif match_str == "8":
                                        total_x8 +=1
                                    elif match_str == "16":
                                        total_x16 +=1
                                    elif match_str == "32":
                                        total_x32 +=1
            
            fain_ocupation[gate_name]["TOTAL-X2"] = total_x2
            fain_ocupation[gate_name]["TOTAL-X4"] = total_x4
            fain_ocupation[gate_name]["TOTAL-X8"] = total_x8
            fain_ocupation[gate_name]["TOTAL-X16"] = total_x16
            fain_ocupation[gate_name]["TOTAL-X32"] = total_x32
            
        return fain_ocupation