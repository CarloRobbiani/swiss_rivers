import os
import pandas as pd
from hydro_to_meteo import Hydro2MeteoMapper


#class with functions to read all the text files
class Read_txt:

    #read in all the air temperature files and write it into one dataframe
    def read_air_temp(folder_path):

        files = os.listdir(folder_path)

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
    def get_air_betw(station, start_date, end_date, air_df, gap_length, adj_list):

        if type(start_date) == str and type(end_date) == str:
            dt_start = start_date[0:10].replace("-", "")
            dt_end = end_date[0:10].replace("-", "")
        else:
            dt_start = start_date.strftime("%Y%m%d")
            dt_end = end_date.strftime("%Y%m%d")

        h2m = Hydro2MeteoMapper()

        air_station = (h2m.meteo(str(station)))

        air_df_st = air_df.loc[(air_df['stn'] == air_station)]
        air_df_st = air_df_st[air_df_st["time"].between(int(dt_start), int(dt_end), inclusive="left")]
        only_numeric = pd.to_numeric(air_df_st["tre200d0"], errors='coerce').notnull().all() #check if value is "-"
        if not only_numeric or len(air_df_st["tre200d0"]) < gap_length:
            neighbour = adj_list[station][0]
            air_array = Read_txt.get_air_betw(neighbour, start_date, end_date, air_df, gap_length, adj_list)
            return air_array
        return air_df_st["tre200d0"].to_numpy()
        
    

if __name__ == "__main__":
  
    air_df = Read_txt.read_air_temp("air_temp")
    air_df.head()

