import os
import pandas as pd
from txt_to_csv import Gaps
from hydro_to_meteo import Hydro2MeteoMapper
from datetime import datetime

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
    #Function that takes a station and two dates (in date format) and returns the values
    #form the air station between those dates as a numpy array
    def get_air_betw(station, start_date, end_date, air_df):

        if type(start_date) == str and type(end_date) == str:
            dt_start = start_date[0:10].replace("-", "")
            dt_end = end_date[0:10].replace("-", "")
        else:
            dt_start = start_date.strftime("%Y%m%d")
            dt_end = end_date.strftime("%Y%m%d")

        h2m = Hydro2MeteoMapper()

        air_station = (h2m.meteo(str(station)))

        air_df = air_df.loc[(air_df['stn'] == air_station)]
        air_df = air_df[air_df["time"].between(int(dt_start), int(dt_end), inclusive="left")]
        return air_df["tre200d0"].to_numpy()
        
    

import pyarrow as pa
import pyarrow.parquet as pq
class read_parquet:

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

            
            file_name = str(file)[:-4]
            path = folder_save_path + "/" + file_name + ".parquet"

            table = pa.Table.from_pandas(df)
            pq.write_table(table, path)
            #df.to_csv(path, sep=";", index = False)



if __name__ == "__main__":

    read_parquet.fill_gaps("hydro_data/Temp", "parquet_hydro/Temp")

