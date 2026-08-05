import os

def get_files(designs_path):

    circuits_list = []
    files = os.listdir(designs_path)

    for file in files:
        circuits_list.append(file)
        print(f"File {file} ad to circuit list")

    return circuits_list
    
def search_file(file_name: str, dir_path):
    files = os.listdir(dir_path)

    for file in files:
        if file == file_name:
            return os.path.join(dir_path, file)
    
    raise FileNotFoundError(f"File {file_name} not found in {dir_path}")