import re

class Read_timing:
    def __init__(self, sta_file):
        self.sta_file = sta_file 
        
    def get_arrival_times(self):
        arrivals = {}
        path_id = 0
        current_arrival = None
        inside_path = False

        with open(self.sta_file, "r") as f:
            for line in f:
                line = line.strip()

                if line.startswith("Startpoint:"):
                    # salva o caminho anterior
                    if current_arrival is not None:
                        arrivals[path_id] = current_arrival

                    path_id += 1
                    current_arrival = None
                    inside_path = True

                elif "data arrival time" in line and inside_path:
                    if current_arrival is None:  # pega só o primeiro
                        value = float(line.split()[0])
                        if value > 0:
                            current_arrival = value

            # salva o último caminho
            if current_arrival is not None:
                arrivals[path_id] = current_arrival

        return arrivals

    def get_cells(self):
        pcritic_id = 0
        result = {}

        pattern_cells = re.compile(r"(_\d+_)/")

        with open(self.sta_file, "r") as f:
            for line in f:
                line = line.strip()

                if line.startswith("Startpoint"):
                    pcritic_id += 1
                    result[pcritic_id] = []
                    continue

                match = pattern_cells.search(line)
                if match and pcritic_id > 0:
                    result[pcritic_id].append(match.group(1))  

        return result

    def count_ocurence_path(self):
        result = {}

        pattern_cells = re.compile(r"(_\d+_)/")

        with open(self.sta_file, "r") as f:
            for line in f:
                line = line.strip()

                match = pattern_cells.search(line)
                if match:
                    cell_id = match.group(1)

                    if cell_id not in result:
                        result[cell_id] = 0

                    result[cell_id] += 1
                
                # A primeira aparição de "data arrival time" marca o fim
                # da listagem de portas do primeiro caminho crítico.
                if "data arrival time" in line:
                    break
                    
        return result
    
    # retorna a ocorência de um dado gate em todos os caminhos críticos do sta
    def ocurence_by_paths(self):
        result = {}
        pattern_cells = re.compile(r"(_\d+_)/")

        with open(self.sta_file, "r") as f:
            for line in f:
                line = line.strip()

                match = pattern_cells.search(line)
                if match:
                    cell_id = match.group(1)

                    if cell_id not in result:
                        result[cell_id] = 0

                    result[cell_id] += 1

        return result
    
    def get_power(self):
        
        pattern = re.compile(r'^Total\s+(?:\S+\s+){3}(\S+)', re.MULTILINE)
    
        with open(self.sta_file, 'r') as f:
            content = f.read()
        
        match = pattern.search(content)
        
        if match:
            power = float(match.group(1))
            return power
        else:
            return None
                





