class Transitions:
    def __init__(self, combinations_list: list, number_gates: int):
        self.combinations_list = combinations_list
        self.number_gates = number_gates

    def replace_size_list(self, source_list: list, gate_index: int, to_replace: str):
        new_list = source_list.copy()
        new_list[gate_index] = to_replace.upper()
        return new_list

    def make_pairs(self, to_size: str, gate: int):
        # Determina o índice real na lista
        if gate <= self.number_gates:
            index_to_size = -gate - 1  # ajuste para índice negativo correto
        else:
            raise ValueError("index out of range")

        # Define o size anterior
        if to_size == "X2":
            previous_size = "X1"
        elif to_size == "X4":
            previous_size = "X2"
        else:
            raise ValueError("Size inválido")

        pairs = []
        for comb in self.combinations_list:
            # Cria a versão anterior trocando só o gate atual
            previous_comb = self.replace_size_list(comb, index_to_size, previous_size)
            pairs.append((comb, previous_comb))

        return pairs