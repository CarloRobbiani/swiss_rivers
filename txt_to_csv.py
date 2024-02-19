import pandas as pd
import os
from collections import Counter


class Read_txt():

    #read in all the air temperature files and write it into one dataframe
    def read_air_temp(folder_path):

        files = os.listdir(folder_path)

        #init list of dataframes
        dfs = []


        for file in files:

            if file.endswith("legend.txt"):
                continue #skip

            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path, delimiter=';')

            dfs.append(df)

        final_df = pd.concat(dfs, ignore_index=True)
        return final_df

    #read in all hydro data
    def read_hydro(folder_path):
        files = os.listdir(folder_path)

        dfs = []

        for file in files:

            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path, delimiter=';', skiprows=8, encoding="iso-8859-1")

            dfs.append(df)

        final_df = pd.concat(dfs, ignore_index=True)
        return final_df

def missing(df, column):
    #longest_seq = 0
    seq_list = []
    current_seq = 0

    for value in df[column].isnull():
        if value:
            current_seq+=1
            #longest_seq = max(longest_seq, current_seq)
        else:
            if(current_seq > 0):
                seq_list.append(current_seq)
            current_seq = 0

    if(current_seq > 0):
        seq_list.append(current_seq)

    len_counts = Counter(seq_list)
    len_counts_sorted = dict(sorted(len_counts.items()))
    
    print("Occurrences of different gap lengths:")
    for length, count in len_counts_sorted.items():
        print(f"Length {length}: {count} occurrences")
