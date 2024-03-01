import pandas as pd
import os
from collections import Counter

#class with functions to read all the text files
class Read_txt:

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


class Gaps():
    #Method that returns the different gap length occurences
    #column: column in which the missing values are
    def missing_len(df, column, do_print):
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
        
        if do_print:
            print("Occurrences of different gap lengths:")
            for length, count in len_counts_sorted.items():
                print(f"Length {length}: {count} occurrences")
        return len_counts_sorted
        


    #Method to find out what dates have missing values in the dataset of hydro data
    #Assumes the dates are there
    def miss_date(df):
        
        # Convert 'Zeitstempel' column to datetime type
        df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'])

        # Find all rows where 'Wert' column has missing values
        missing_values_dates = df.loc[df['Wert'].isna(), 'Zeitstempel']
        return missing_values_dates

    #Problem: slow af
    #Method used on the dataframe where the rows are missing in order to fill them up
    def find_missing_dates(df):
        min_date = "1980-01-01 00:00:00"
        #min_date = df['Zeitstempel'].min()
        max_date = df['Zeitstempel'].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
        existing_dates = pd.to_datetime(df['Zeitstempel']).dt.date.unique()
        missing_dates = [date for date in all_dates if date.date() not in existing_dates]
        return missing_dates

    #Method that takes the hydro data and adds NaN for the column "Wert" entries where there are no dates
    #File_list: Folder with the original temp/flow data
    #folder_save_path: the folder where the data should be saved to
    def fill_gaps(file_list, folder_save_path):
        for file in os.listdir(file_list):
            file_path = file_list + "/" + file
            df = pd.read_csv(file_path, skiprows=8, delimiter=";", encoding="latin1")
            missings = Gaps.find_missing_dates(df)

            for date in missings:
                new_row = {'Stationsname': df.iloc[:,0].iloc[0],
            'Stationsnummer': df.iloc[:,1].iloc[0],
            'Parameter': df.iloc[:,2].iloc[0],
            'Zeitreihe': df.iloc[:,3].iloc[0],
            'Parametereinheit': df.iloc[:,4].iloc[0],
            'Gewässer': df.iloc[:,5].iloc[0],
            'Zeitstempel': str(date),
            'Zeitpunkt_des_Auftretens': None,
            'Wert': None,
            'Freigabestatus': "hinzugefügte Daten"}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            path = folder_save_path + "/" + str(file)
            df.to_csv(path, sep=";", index = False)