from neighbours import Neighbour
import os
import pandas as pd
from txt_to_csv import Gaps, Read_txt
from datetime import datetime, timedelta
from reading import Read_txt
import numpy as np

from filling_main import interpolate
from models import Model
    
exception_stations = [2617, 2612, 2462, 2167, 2068]
class fillers:

    #This function is only for visualization purposes
    def fill_interpolation(station):
        
        df = pd.read_csv(f"filled_hydro/Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        #df = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        df = df.sort_values(by="Zeitstempel")
        output_df = df.set_index("Zeitstempel")
        missing_dates_df = Gaps.gaps_with_dates(station, "filled_hydro")

        for index, row in missing_dates_df.iterrows():
            start_date = row["start_date"]
            end_date = row["end_date"]
            gap_length = row["gap_length"]
            date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))
            value_list = []

            temperature = interpolate(df, start_date, end_date)
            for date in date_range:
                output_df.loc[str(date), "Wert"] = temperature

        output_df.to_csv(f"predictions/{station}/Temp_{station}_interpolation.csv", index=False)
    

    #fills in gaps only with air temperature
    def fill_a2gap(station, adj_list, file_list, save_path):

        air_df = Read_txt.read_air_temp("air_temp")

        if station == -1:
            return -1

        model_at = Model(station, "at2wt", 1)

        df = pd.read_csv(f"{file_list}/Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        #df = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        df = df.sort_values(by="Zeitstempel")
        output_df = df.set_index("Zeitstempel")
        missing_dates_df = Gaps.gaps_with_dates(station, file_list)

        for index, row in missing_dates_df.iterrows():
            start_date = row["start_date"]
            end_date = row["end_date"]
            gap_length = row["gap_length"]
            date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))
            value_list = []

            if gap_length < 3:
                temperature = interpolate(df, start_date, end_date)
                for date in date_range:
                    output_df.loc[str(date), "Wert"] = temperature
                continue
            
            value_list = Read_txt.get_air_betw(station, start_date + timedelta(days=1), end_date, air_df, gap_length, adj_list)
                
            value_at = model_at.a2gap(value_list)

            array_value = value_at.detach().numpy()

            output_df.loc[str(start_date+ timedelta(days=1)): str(end_date - timedelta(days=1)),"Wert"] = array_value
        output_df.reset_index(inplace=True)
        output_df.to_csv(f"{save_path}/{station}/Temp_{station}_a.csv", index=False)
        #output_df.to_csv("temp.csv", index=False)

    #fills in gaps with air temperature and discharge
    def fill_aq2gap(station, adj_list, file_list, save_path):
        air_df = Read_txt.read_air_temp("air_temp")

        if station == -1:
            return -1

        model_atq = Model(station, "atq2wt", 2)

        df_flow = pd.read_csv(f"{file_list}\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")
        #df_flow = pd.read_parquet(f"parquet_hydro\Flow/{station}_Abfluss_Tagesmittel.parquet")
        df_flow = df_flow.sort_values(by="Zeitstempel")
        df_temp = pd.read_csv(f"{file_list}\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        #df_temp = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        df_temp = df_temp.sort_values(by="Zeitstempel")
        df_temp["Flow"] = df_flow["Wert"].to_numpy()
        output_df = df_temp.set_index("Zeitstempel")
        missing_dates_df = Gaps.gaps_with_dates(station, file_list)

        for index, row in missing_dates_df.iterrows():
            start_date = row["start_date"]
            end_date = row["end_date"]
            gap_length = row["gap_length"]
            date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))
            value_list = []

            if gap_length < 3:
                temperature = interpolate(df_temp, start_date, end_date)
                for date in date_range:
                    output_df.loc[str(date), "Wert"] = temperature
                continue

            date_list = Gaps.consecutive_non_missing(df_temp, str(start_date), str(end_date), ["Flow"])

            for start, end in date_list:
                if start == end:
                    continue # All rows have some missing data
                start_d = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                end_d = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                gap_l = (end_d - start_d).days
                flow_list = df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)]["Flow"]
                value_list = Read_txt.get_air_betw(station, start, end, air_df, gap_l, adj_list)
                
                value_wt = model_atq.aq2gap(value_list, flow_list)

                array_value = value_wt.detach().numpy()

                
                output_df.loc[str(start): str(end_d - timedelta(days=1)),"Wert"] = array_value
        output_df.reset_index(inplace=True)
        output_df.to_csv(f"{save_path}/{station}/Temp_{station}_aq.csv", index=False)
        #output_df.to_csv("temp_q.csv", index=False)

    
    def fill_aqn2gap(station, adj_list, file_list, save_path):

        cols = ["Flow"] #columns to check for missing data
        air_df = Read_txt.read_air_temp("air_temp")
        df_temp = pd.read_csv(f"{file_list}\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        df_temp = df_temp.sort_values(by="Zeitstempel")

        if station == -1 or station not in adj_list: #if station has no neighbours i.e. only connected to -1
            df_temp.to_csv(f"{save_path}/{station}/Temp_{station}_aqn.csv", index=False)
            return -1
        
        model_atq = Model(station, "atqn2wt", len(adj_list[station])+2)

        df_flow = pd.read_csv(f"{file_list}\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")
        #df_flow = pd.read_parquet(f"parquet_hydro\Flow/{station}_Abfluss_Tagesmittel.parquet")
        df_flow = df_flow.sort_values(by="Zeitstempel")
        #df_temp = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        
        df_temp["Flow"] = df_flow["Wert"].to_numpy()
        for n in adj_list[station]:
            df_n = pd.read_csv(f"{file_list}\Temp/{n}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
            df_n = df_n.sort_values(by="Zeitstempel")
            df_temp[df_n["Stationsnummer"][0]] = df_n["Wert"].to_numpy()
            cols.append(df_n["Stationsnummer"][0])

        output_df = df_temp.set_index("Zeitstempel")
        missing_dates_df = Gaps.gaps_with_dates(station, file_list)

        for index, row in missing_dates_df.iterrows():
            start_date = row["start_date"]
            end_date = row["end_date"]
            gap_length = row["gap_length"]
            date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))
            value_list = []

            if gap_length < 3:
                temperature = interpolate(df_temp, start_date, end_date)
                for date in date_range:
                    output_df.loc[str(date), "Wert"] = temperature
                continue

            #date_list = Gaps.consecutive_non_missing_with_neighbours(df_temp, str(start_date), str(end_date), cols)
            date_list = Gaps.consecutive_non_missing(df_temp, str(start_date), str(end_date), cols)

            #for start, end, missing_cols in date_list:
            for start, end in date_list:
                if start == end:
                    continue # All rows have some missing data
                start_d = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                end_d = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                gap_l = (end_d - start_d).days
                n_list = []
                flow_list = df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)]["Flow"]
                value_list = Read_txt.get_air_betw(station, start, end, air_df, gap_l, adj_list)

                """ for n in adj_list[station]:
                    if n not in missing_cols: """
                n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][n])
                
                
                value_wt = model_atq.aqn2gap(value_list, flow_list, n_list)
                array_value = value_wt.detach().numpy()
                output_df.loc[str(start): str(end_d-timedelta(days=1)),"Wert"] = array_value

        output_df.reset_index(inplace=True)
        output_df.to_csv(f"{save_path}/{station}/Temp_{station}_aqn.csv", index=False)


    def fill_aqn2gap_special(station, adj_list, file_list, save_path):

        cols = ["Flow"] #columns to check for missing data
        air_df = Read_txt.read_air_temp("air_temp")
        special_n = Neighbour.alter_neighbour(station) #TODO always return list

        #TODO check if list
        if station == -1 or not special_n:#special_n == 0:#if there is no special case for this station skip it
            return -1

        df_flow = pd.read_csv(f"{file_list}\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")
        #f_flow = pd.read_parquet(f"parquet_hydro\Flow/{station}_Abfluss_Tagesmittel.parquet")
        df_flow = df_flow.sort_values(by="Zeitstempel")
        #df_temp = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        df_temp = pd.read_csv(f"{file_list}\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        df_temp = df_temp.sort_values(by="Zeitstempel")
        df_temp["Flow"] = df_flow["Wert"].to_numpy()
        """ for n in adj_list[station]:
            if n == -1:
                continue
            df_n = pd.read_csv(f"{file_list}\Temp/{n}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
            df_n = df_n.sort_values(by="Zeitstempel")
            df_temp[df_n["Stationsnummer"][0]] = df_n["Wert"].to_numpy()
            #cols.append(df_n["Stationsnummer"][0]) """

        for special_station in special_n:
            df_n = pd.read_csv(f"{file_list}\Temp/{special_station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
            df_n = df_n.sort_values(by="Zeitstempel")
            df_temp[df_n["Stationsnummer"][0]] = df_n["Wert"].to_numpy()
            cols.append(df_n["Stationsnummer"][0])

        output_df = df_temp.set_index("Zeitstempel")
        missing_dates_df = Gaps.gaps_with_dates(station, file_list)

        for index, row in missing_dates_df.iterrows():
            start_date = row["start_date"]
            end_date = row["end_date"]
            gap_length = row["gap_length"]
            date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))
            value_list = []

            if gap_length < 3:
                temperature = interpolate(df_temp, start_date, end_date)
                for date in date_range:
                    output_df.loc[str(date), "Wert"] = temperature
                continue

            #Check if one or more neighbours are missing and ignore them 
            #date_list = Gaps.consecutive_non_missing_with_neighbours(df_temp, str(start_date), str(end_date), cols[-1])

            date_list = Gaps.consecutive_non_missing(df_temp, str(start_date), str(end_date), cols)
            

            for start, end in date_list:
                if start == end:
                    continue # All rows have some missing data
                start_d = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                end_d = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                gap_l = (end_d - start_d).days
                n_list = []
                flow_list = df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)]["Flow"]
                value_list = Read_txt.get_air_betw(station, start, end, air_df, gap_l, big_adj)

                for special_station in special_n:
                    #n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][cols[-1]])
                    n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][special_station])
                model_atq = Model(station, "atqn2wt_special", len(special_n)+2)
                #model_atq = Model(station, "atqn2wt_special", len(special_n))#TODO check if it is a list

                """ for n in adj_list[station]:
                    if n not in missing_cols:
                        n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][n])
                
                if n_list == []: #if list is empty add special neighbour and load special model
                    n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][cols[-1]])
                    model_atq = Model(station, "atqn2wt_special", 3) #TODO Add these models, is not yet working
                else:
                    #model_atq = Model(station, "atqn2wt", len(adj_list[station])+2)
                    continue """

                value_wt = model_atq.aqn2gap(value_list, flow_list, n_list)
                array_value = value_wt.detach().numpy()
                output_df.loc[str(start): str(end_d-timedelta(days=1)),"Wert"] = array_value

        output_df.reset_index(inplace=True)
        output_df.to_csv(f"{save_path}/{station}/Temp_{station}_aqn_special.csv", index=False)
    
    #returns the final estimation of the df
    #TODO consider seperate Label for special cases
    def return_final_df(station, file_path, save_path, include_special):
        df = pd.read_csv(f"filled_hydro\Temp\{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        df = df.sort_values(by="Zeitstempel")
        df = df.set_index("Zeitstempel")
        df_a = pd.read_csv(f"{file_path}\{station}\Temp_{station}_a.csv")
        df_a = df_a.sort_values(by="Zeitstempel")
        df_a = df_a.set_index("Zeitstempel")
        df_aq = pd.read_csv(f"{file_path}\{station}\Temp_{station}_aq.csv")
        df_aq = df_aq.sort_values(by="Zeitstempel")
        df_aq = df_aq.set_index("Zeitstempel")
        df_aqn = pd.read_csv(f"{file_path}\{station}\Temp_{station}_aqn.csv")
        df_aqn = df_aqn.sort_values(by="Zeitstempel")
        df_aqn = df_aqn.set_index("Zeitstempel")
        df["Model"] = "Source"

        df.loc[df["Wert"].isna(), "Model"] = "AQN2Gap"
        df["Wert"] = df["Wert"].fillna(df_aqn["Wert"])

        if include_special and os.path.exists(f"{file_path}\{station}\Temp_{station}_aqn_special.csv"):
            df_aqns = pd.read_csv(f"{file_path}\{station}\Temp_{station}_aqn_special.csv")
            df_aqns = df_aqns.sort_values(by="Zeitstempel")
            df_aqns = df_aqns.set_index("Zeitstempel")
            df.loc[df["Wert"].isna(), "Model"] = "AQN2Gap_special"
            df["Wert"] = df["Wert"].fillna(df_aqns["Wert"])

        df.loc[df["Wert"].isna(), "Model"] = "AQ2Gap"
        df["Wert"] = df["Wert"].fillna(df_aq["Wert"])

        df.loc[df["Wert"].isna(), "Model"] = "A2Gap"
        df["Wert"] = df["Wert"].fillna(df_a["Wert"])

        df.reset_index(inplace=True)
        df.to_csv(f"{save_path}/{station}/Temp_final_{station}.csv", index=False)





if __name__ == "__main__":


    big_adj = Neighbour.all_adj_list()
    
    """ for st in os.listdir("models"):
        fillers.fill_a2gap(int(st), big_adj, "filled_hydro", "predictions")
        fillers.fill_aq2gap(int(st), big_adj, "filled_hydro", "predictions")
        fillers.fill_aqn2gap(int(st), big_adj, "filled_hydro", "predictions")
        fillers.fill_aqn2gap_special(int(st), big_adj, "filled_hydro", "predictions")  """
    
    
    for st in os.listdir("models"):
        fillers.return_final_df(int(st), "predictions", "predictions", False) 
    
