class Netlist_and_path:

    def __init__(self):
        self.nets_and_path = {}

    def add_values(self, key) -> None:
        self.nets_and_path[key] = {
            "LOGIC-TYPE": "",
            "PATH-OCURENCE": 0,
            "PATHS-OCURENCE": 0,
            "FA-IN": 0,
            "FA-OUT": 0,
            "LOGIC-LEVEL": 0,
            "DEEP": 0,
            "LOADED-CELLS": 0
        }

class Manipulet_dict(Netlist_and_path):

    def __init__(self):
        super().__init__()

    def fild_dictionary(self, cells_id_list: list, logic_type_list: list) -> None:
        for key, logic_type in zip(cells_id_list, logic_type_list):
            self.add_values(key)
            self.nets_and_path[key]["LOGIC-TYPE"] = logic_type

    def ad_fanin(self, key: int, fanin: int) -> None:
            self.nets_and_path[key]["FA-IN"] = fanin

    def ad_fanout(self, key: int, fanout: int) -> None:
        self.nets_and_path[key]["FA-OUT"] = fanout

    def ad_logic_level(self, key: int, logic_level: int) -> None:
        self.nets_and_path[key]["LOGIC-LEVEL"] = logic_level

    def ad_deep(self, key: int, deep: int) -> None:
        self.nets_and_path[key]["DEEP"] = deep

    def ad_path_occurrence(self, key: int, occurrence: int) -> None:
        self.nets_and_path[key]["PATH-OCURENCE"] = occurrence
    
    def ad_loaded(self, key: int, loaded: int) -> None:
        self.nets_and_path[key]["LOADED-CELLS"] = loaded
