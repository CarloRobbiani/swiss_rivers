import pandas as pd
import os


#read in all the air temperature files and write it into one dataframe
def read_air_temp(folder_path):
#list all files from directory
    files = os.listdir(folder_path)

    #init list of dataframes
    dfs = []

    #loop through files
    for file in files:

        if file.endswith("legend.txt"):
            continue #skip

        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path, delimiter=';')

        dfs.append(df)

    final_df = pd.concat(dfs, ignore_index=True)
    return final_df

def read_flow(folder_path):
    files = os.listdir(folder_path)

    #init list of dataframes
    dfs = []

    #loop through files
    for file in files:

        #TODO Change this to read the files only from line 9

        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path, delimiter=';')

        dfs.append(df)

    final_df = pd.concat(dfs, ignore_index=True)
    return final_df
