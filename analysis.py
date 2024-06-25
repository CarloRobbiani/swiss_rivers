import pandas as pd
import os
import re
import json
import statistics

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
        df.replace("AQN2Gap_special", "AQN2Gap", inplace=True)
        models.extend(df["Model"].tolist())

    total_len = len(models)

    for m in model_names:
        m_list = [mod for mod in models if m == mod]
        len_m = len(m_list)
        p = len_m / total_len * 100
        print(f"Model {m} precentage: {p}")

#calculates the average RMSE over all predictions
#TODO consider special cases
def calculate_RMSE(prediction_folder):
    station_RMSE = []
    total_len = 0
    final_RMSE = 0
    for station in os.listdir(prediction_folder):
        RMSE_list = []
        final_df = pd.read_csv(f"{prediction_folder}/{station}/Temp_final_{station}.csv", delimiter=",", dtype={"Model": str})
        metadata_folder = f"models/{station}"
        prefix_list = [f"{station}_at2wt", f"{station}_atq2wt", f"{station}_atqn2wt_T", f"{station}_atqn2wt_special"]

        aqn = final_df[final_df["Model"] == "AQN2Gap"]["Model"]
        aq = final_df[final_df["Model"] == "AQ2Gap"]["Model"]
        a = final_df[final_df["Model"] == "A2Gap"]["Model"]
        aqn_special = final_df[final_df["Model"] == "AQN2Gap_special"]["Model"]
        
        total_len += len(aqn) + len(aq) + len(a) + len(aqn_special)

        for prefix in prefix_list:

            filename = [filename for filename in os.listdir(metadata_folder) if filename.startswith(prefix)]
            if filename == []:
                RMSE_list.append(0)
                continue #the special file does not exist
            f = open(metadata_folder + "/" + str(filename[-1]))
            metadata = json.load(f)
            rmse = metadata["test_result"]["rmse"]
            RMSE_list.append(rmse)
        final_RMSE += (RMSE_list[0] * len(a) + RMSE_list[1] * len(aq) + RMSE_list[2] * len(aqn) + RMSE_list[3] * len(aqn_special))

    avg_RMSE = final_RMSE/total_len
    print(avg_RMSE)



if __name__ == "__main__":
    #get_percentages()
    calculate_RMSE("predictions")
    #print(find_missing_stations("filled_hydro\Temp", "models"))