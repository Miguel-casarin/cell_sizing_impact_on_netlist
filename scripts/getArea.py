import json

class Get_Area:

    def __init__(self, json_library):
        self.json_library = json_library

    # retorna a area celula passando a string "LOGIC-TYPE_DRIVE-STANGE"
    def search_area(self, cell: str) -> float:
        with open(self.json_library, "r") as f:
            areas = json.load(f)
        return areas.get(cell, None)

    def return_previos_drive(self, drive: str) -> str:
        size_map = {"X32": "X16", "X16": "X8", "X8": "X4", "X4": "X2", "X2": "X1", "X1": None}

        for size, prev_size in size_map.items():
            if drive.endswith(size):
                if prev_size is None:
                    return "X1"
                return prev_size

    def return_total_area(self, gates_list) -> float:
        total_area = 0.0
        for cell in gates_list:
            total_area += self.search_area(cell)
        return total_area

    def previos_list(self, current_comb_list: list) -> list:
        previos = []
        for i in current_comb_list:
            p = self.return_previos_drive(i)
            previos.append(p)
        return previos

    def cost(self, current_value: float, previos_value: float) -> float:
        return current_value - previos_value
    


