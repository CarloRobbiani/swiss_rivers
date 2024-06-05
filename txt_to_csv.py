import pandas as pd
import os
from collections import Counter
import datetime
from fastparquet import ParquetFile
from itertools import groupby

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

    def read_filled_hydro():
        files = os.listdir("filled_hydro/Temp")

        dfs = []

        for file in files:

            file_path = os.path.join("filled_hydro/Temp", file)
            df = pd.read_csv(file_path, delimiter=';', encoding="latin1")

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
        df.sort_values(by="Zeitstempel")

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
        df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'])

        # Find all rows where 'Wert' column has missing values
        missing_values_dates = df.loc[df['Wert'].isna(), 'Zeitstempel']
        return missing_values_dates

    #function that returns df with information of gap lenght and start and end time of gap
    #returns df with columns [start_date, end_date, gap_length]
    #start date is the day before the gap, end date the day after the gap ends
    def gaps_with_dates(station, save_path):
        df = pd.read_csv(f"{save_path}\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        #pf = ParquetFile(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        #df = pf.to_pandas()
        df["Zeitstempel"] = pd.to_datetime(df['Zeitstempel'])
        df = df.sort_values(by="Zeitstempel")
        #df.set_index("Zeitstempel", inplace=True)

        missing_data = df['Wert'].isnull()

        gap_lengths = []
        start_dates = []
        end_dates = []


        consecutive_missing = []
        for k, g in groupby(enumerate(missing_data), lambda x: x[1]):
            if k:
                consecutive_missing.append(list(map(lambda x: x[0], list(g))))

        for entry in consecutive_missing:

            start_dates.append(df.iloc[entry[0]]["Zeitstempel"] - datetime.timedelta(days=1))
            end_dates.append(df.iloc[entry[-1]]["Zeitstempel"] + datetime.timedelta(days=1))
            gap_lengths.append(len(entry))

        gap_df = pd.DataFrame({
            'start_date': start_dates,
            'end_date': end_dates,
            'gap_length': gap_lengths
        })
        
        return gap_df
    
    #Returns an array with dates where in between there are no missing values in the specified columns
    #returns an array of the form [('1980-01-01 00:00:00', '1982-12-31 00:00:00'), ('1983-01-02 00:00:00', '1990-01-01 00:00:00')]
    def consecutive_non_missing(df, start_date, end_date, column_names):

        df = df.sort_values(by="Zeitstempel")
        #df = df.set_index("Zeitstempel")
        df_filtered = df[(df["Zeitstempel"] >= start_date) & (df["Zeitstempel"] <= end_date)]
    
        df_filtered.reset_index(drop=True, inplace=True)
        
        consecutive_blocks = []
        start = None
        end = None
        
        for i in range(len(df_filtered)):
            if all(pd.notna(df_filtered.loc[i, col]) for col in column_names):
                if start is None:
                    start = df_filtered.loc[i, 'Zeitstempel']
                end = df_filtered.loc[i, 'Zeitstempel']
            else:
                if start is not None:
                    consecutive_blocks.append((start, end))
                    start = None
                    end = None
        
        # Check if the last block extends to the end of the DataFrame
        if start is not None:
            consecutive_blocks.append((start, end))
        
        return consecutive_blocks
    
    #returns the consecutive blocks in df but also allows that some neighbours are missing
    def consecutive_non_missing_with_neighbours(df, start_date, end_date, column_names):

        df = df.sort_values(by="Zeitstempel")
        #df = df.set_index("Zeitstempel")
        df_filtered = df[(df["Zeitstempel"] >= start_date) & (df["Zeitstempel"] <= end_date)]
    
        df_filtered.reset_index(drop=True, inplace=True)
        
        consecutive_blocks = []
        start = None
        end = None
        missing_columns = set()
        nr_of_neighbours = len(column_names) - 1
        neighbour_cols = column_names[-nr_of_neighbours:]

        for i in range(len(df_filtered)):
            missing_cols_for_row = set(col for col in neighbour_cols if pd.isna(df_filtered.loc[i, col]))
            if nr_of_neighbours - 1 >= len(missing_cols_for_row) >= 1 and (start is None or missing_cols_for_row == missing_cols):
                if start is None:
                    start = df_filtered.loc[i, 'Zeitstempel']
                end = df_filtered.loc[i, 'Zeitstempel']
                
                if len(missing_cols_for_row) == 0:
                    missing_cols = None
                else:
                    missing_cols = missing_cols_for_row
            else:
                if start is not None:
                    consecutive_blocks.append((start, end, missing_cols))
                    start = None
                    end = None
        # Check if the last block extends to the end of the DataFrame
        if start is not None:
            consecutive_blocks.append((start, end, missing_cols))

        return consecutive_blocks
        

    
    def find_gap_length(station, date):
        if station == -1:
            return -1

        gap_df = Gaps.gaps_with_dates(station)

        gap_df['start_date'] = pd.to_datetime(gap_df['start_date'])
        gap_df['end_date'] = pd.to_datetime(gap_df['end_date'])
        gap_df['end_date'] += pd.Timedelta(days=1)

        # Create boolean mask to filter rows where the date is within the range
        mask = (date >= gap_df['start_date']) & (date <= gap_df['end_date'])

        # Use boolean indexing to filter rows and get the gap_length
        matching_gaps = gap_df[mask]

        if not matching_gaps.empty:
            return matching_gaps.iloc[0]['gap_length']
        else:
            return -1
        
    #Problem: slow af
    #Method used on the dataframe where the rows are missing in order to fill them up
    def find_missing_dates(df):
        min_date = "1980-01-01 00:00:00"
        #min_date = df['Zeitstempel'].min()
        #max_date = df['Zeitstempel'].max()
        max_date = "2020-12-31 00:00:00"
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