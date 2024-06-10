import pandas as pd
import os
import re

#find out what stations are missing in the specified folder path
def find_missing_stations(files_path, folder_path):
    numbers = set()
    for filename in os.listdir(files_path):
        match = re.match(r'^(\d{4})', filename)
        if match:
            numbers.add(match.group(1))
    
    folders = set(name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name)))
       
    missing_numbers = numbers - folders
    return missing_numbers


#get the percentages of usage for each model in the final prediction files
def get_percentages():

    model_names = ["A2Gap", "AQ2Gap", "AQN2Gap"]
    models = []

    stations = os.listdir("predictions")
    for st in stations:
        df = pd.read_csv(f"predictions\{st}/Temp_final_{st}.csv", delimiter=",")
        df = df[df["Model"] != "Source"]
        models.extend(df["Model"].tolist())

    total_len = len(models)

    for m in model_names:
        m_list = [mod for mod in models if m == mod]
        len_m = len(m_list)
        p = len_m / total_len * 100
        print(f"Model {m} precentage: {p}")


if __name__ == "__main__":
    get_percentages()
    #print(find_missing_stations("filled_hydro\Temp", "models"))