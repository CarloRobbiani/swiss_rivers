import pandas as pd
import os
from collections import Counter

#class with functions to read all the text files
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

#Method that returns the different gap length occurences
#column: column in which the missing values are
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


#Method to find out what dates are missing in the dataset of hydro data
def miss_date(df):
    df["Zeitstempel"] = pd.to_datetime(df["Zeitstempel"])

    date_range = pd.date_range(start = df["Zeitstempel"].min(), end=df["Zeitstempel"].max())
    missing_dates = df.groupby("Stationsnummer").apply(lambda x: date_range.difference(x["Zeitstempel"])).reset_index()
    missing_dates.columns = ["Stationsnummer", "missing_dates"]

    missing_dates["missing_dates"] = missing_dates["missing_dates"].apply(lambda x: None if len(x) == 0 else x)

    print(missing_dates)
    return missing_dates

#Problem: slow af
def find_missing_dates(df):
    min_date = df['Zeitstempel'].min()
    max_date = df['Zeitstempel'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
    existing_dates = pd.to_datetime(df['Zeitstempel']).dt.date.unique()
    missing_dates = [date for date in all_dates if date.date() not in existing_dates]
    return missing_dates
