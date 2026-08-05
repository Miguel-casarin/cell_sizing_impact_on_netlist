import csv
import os

class Create_table:
    def __init__(self, coluns_list, csv_dir, csv_path):
        self.coluns_list = coluns_list
        self.csv_dir = csv_dir
        self.csv_path = csv_path

    def make_csv(self):
        os.makedirs(self.csv_dir, exist_ok=True)
        with open(self.csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(self.coluns_list)

class Edit_csv:
    def __init__(self, csv_path, data):
        self.csv_path = csv_path
        self.data = data

    def insert_csv_data(self):
        with open(self.csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.data)