class Decoder:
    def __init__(self, total_cells, value_to_decode):
        self.total_cells = total_cells
        self.value_to_decode = value_to_decode

    def total_to_size(self):
        total_combinations = 5 ** self.total_cells
        combinations = []

        for j in range(total_combinations):
            comb = []
            num = j

            for _ in range(self.total_cells):
                comb.append(num % 5)
                num //= 5

            combinations.append(list(reversed(comb)))

        return combinations

    def decode_size(self, string_to_decode):
        mapping = {
            0: "X1",
            1: "X2",
            2: "X4",
            3: "X8",
            4: "X16",
            5: "X32"
        }

        return [mapping[x] for x in string_to_decode]


class Encoder:
    def __init__(self, size_list: list, total_gates: int):
        self.size_list = size_list
        self.total_gates = total_gates

    def encode_size(self):
        mapping = {
            "X1": 0,
            "X2": 1,
            "X4": 2,
            "X8": 3,
            "X16": 4,
            "X32": 5
        }

        return [mapping[x] for x in self.size_list]

    def base6_to_decimal(self):
        """Converte lista em base 5 para número decimal"""
        base5_list = self.encode_size()
        decimal = 0
        for digit in base5_list:
            decimal = decimal * 6 + digit

        return decimal