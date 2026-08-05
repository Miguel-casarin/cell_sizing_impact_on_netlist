import csv

def seach_lower_available(csv_file, colunn: str, blocked_indices: list) -> int:
    lower_value = float("inf")
    lower_indice = None

    with open(csv_file) as f:
        read = csv.DictReader(f)

        for indice, row in enumerate(read, start=1):
            if indice in blocked_indices:
                continue
            value = float(row[colunn])
            if value < lower_value:
                lower_value = value
                lower_indice = indice

    return lower_indice


def return_value(csv_file, colunn, line_indice):

    with open(csv_file) as f:
        read = csv.DictReader(f)

        for indice, row in enumerate(read, start=1):
            if indice == line_indice:
                return float(row[colunn])
    
    return None


def change_value(csv_file, colunn, line_indice, new_value):

    rows = []

    with open(csv_file, newline='') as f:
        read = csv.DictReader(f)

        for indice, row in enumerate(read, start=1):

            if indice == line_indice:
                row[colunn] = new_value

            rows.append(row)

    with open(csv_file, 'w', newline='') as f:
        write = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        write.writeheader()
        write.writerows(rows)