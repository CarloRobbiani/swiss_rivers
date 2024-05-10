from neighbours import Neighbour
import os
import pandas as pd
from txt_to_csv import Gaps, Read_txt
from datetime import datetime, timedelta
import profile
from line_profiler import LineProfiler
from fastparquet import ParquetFile
import torch
from reading import Read_txt
import numpy as np

import numpy as np
from filling_main import interpolate, fill_with_air, return_flow, isnewer
from models import Model

def fill(station, adj_list):
    print(f"Station {station}")

    data = np.load("models/2481\Apr19_20-24-04_bnode051_11243919_1797_normalizers.npy")
    target_low, target_high = map(float, data[0][1:])
    discharge_low, discharge_high = map(float, data[1][1:])
    air_low, air_high = map(float, data[2][1:])
    wt_n_low, wt_n_high = map(float, data[3][1:])


    if station == -1:
        return -1

    #df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
    df = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
    output_df = df.set_index("Zeitstempel")
    #df = pf.to_pandas()
    missing_dates_df = Gaps.gaps_with_dates(station)

    for index, row in missing_dates_df.iterrows():
        start_date = row["start_date"]
        end_date = row["end_date"]
        gap_length = row["gap_length"]
        date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))

        if gap_length < 3:
            #TODO use interpolation
            for date in date_range:
                out = interpolate(df, start_date, end_date)
                print(f"Out interpolation: {out}")
                #TODO change to write in existing dataframe
                output_df.loc[str(date), "Wert"] = out
            
        else:
            #TODO use either air temperature or neighbour + discharge
            neighbour_list = adj_list[station]
            length = len(neighbour_list)

            #TODO make it faster
            for date in date_range:
                #TODO Werte am stück für AQ oder N
                value_list = []
                missing_nr = Neighbour.neighbour_missing(neighbour_list, str(date))
                discharge = return_flow(station, date)
                air_target = fill_with_air(station, date, adj_list)

                #case no missing neighbours
                if missing_nr == 0:
                    values = Neighbour.get_Neighbour_values(station, str(date), adj_list)
                    v_tens = (values[2152])
                    print("No missing Neighbours")
                    #TODO use either AQN2gap or AN2gap
                    #output = Models.atqn2gap(air_low, air_high, air_target, discharge_low, discharge_high, discharge, 
                     #                 target_low, target_high, wt_n_low, wt_n_high, v_tens, station)
                    
                    #output_df.loc[str(date), "Wert"] = output.item()

                    """ new_row = {"Zeitstempel": date, "Wert" : output.item()}
                    dataframe = pd.concat([dataframe, pd.DataFrame([new_row])]) """

                #case  missing neighbours
                elif missing_nr > 0:
                    #TODO consider special cases
                    for neighbour in neighbour_list:
                        #first check if neighbour is not missing
                        gap_len = Gaps.find_gap_length(neighbour, str(date))
                        if gap_len == -1:
                            #maybe not string?
                            value = Neighbour.get_value(neighbour, str(date))
                            value_list.append(value)
                            continue
                        

                        if 0 < gap_len <=2:
                            #interpolate
                            #df_n =  pd.read_csv(f"filled_hydro\Temp/{neighbour}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
                            pf = ParquetFile(f"parquet_hydro\Temp/{neighbour}_Wassertemperatur.parquet")
                            df_n = pf.to_pandas()
                            value = interpolate(df_n, start_date, end_date)
                            print(f"Neighbour {neighbour} temp: {value}")
                            value_list.append(value)


                        elif isnewer(neighbour, str(date)):
                            #If the station is newer than the specified date use the alternative neighbour
                            #TODO treat the case where it is not the new station considered
                            new_n = Neighbour.alter_neighbour(station)
                            if new_n == 0:
                                #ignore this neighbour for now
                                continue
                            pf = ParquetFile(f"parquet_hydro\Temp/{new_n}_Wassertemperatur.parquet")
                            df_n = pf.to_pandas()
                            value = df_n.loc[(df_n['Zeitstempel'] == date)]["Wert"]
                            value_list.append(value)
                            continue

                        #TODO use air temp
                        else:
                            value = fill_with_air(neighbour, date, adj_list)
                            #value_at = Models.a2gap(value, neighbour)
                            #value_list.append(value_at)
                    #TODO use AQN2Gap model or AN2Gap model
                    #output = Models.atqn2gap(air_low, air_high, air_target, discharge_low, discharge_high, discharge, 
                              #        target_low, target_high, wt_n_low, wt_n_high, value_list, station)
                    
                    #print(f"Output: {output}")
                    #output_df.loc[str(date), "Wert"] = output.item()
                    """ new_row = {"Zeitstempel": date, "Wert" : output.item()}
                    dataframe = pd.concat([dataframe, pd.DataFrame([new_row])])
    df = pd.DataFrame(dataframe, columns=["Zeitstempel", "Wert"]) """
    output_df.reset_index(inplace=True)
    output_df.to_csv("temp.csv", index=False)


#fills in gaps only with air temperature maybe add interplolation for short gaps
def fill_a2gap(station, adj_list):
    air_df = Read_txt.read_air_temp("air_temp")

    model_at = Model(station, "at2wt", 1)


    if station == -1:
        return -1

    #df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
    df = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
    df = df.sort_values(by="Zeitstempel")
    output_df = df.set_index("Zeitstempel")
    missing_dates_df = Gaps.gaps_with_dates(station)

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
        
        value_list = Read_txt.get_air_betw(station, start_date + timedelta(days=1), end_date, air_df, gap_length, adj_list)
            
        value_at = model_at.a2gap(value_list)

        array_value = value_at.detach().numpy()

        output_df.loc[str(start_date+ timedelta(days=1)): str(end_date - timedelta(days=1)),"Wert"] = array_value
    output_df.reset_index(inplace=True)
    output_df.to_csv(f"predictions/{station}/Temp_{station}_a.csv", index=False)
    #output_df.to_csv("temp.csv", index=False)

#fills in gaps with air temperature and discharge
def fill_aq2gap(station, adj_list):
    air_df = Read_txt.read_air_temp("air_temp")

    model_atq = Model(station, "atq2wt", 2)
    if station == -1:
        return -1

    #df_flow = pd.read_csv(f"filled_hydro\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")
    df_flow = pd.read_parquet(f"parquet_hydro\Flow/{station}_Abfluss_Tagesmittel.parquet")
    df_flow = df_flow.sort_values(by="Zeitstempel")
    df_temp = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
    df_temp = df_temp.sort_values(by="Zeitstempel")
    df_temp["Flow"] = df_flow["Wert"].to_numpy()
    output_df = df_temp.set_index("Zeitstempel")
    missing_dates_df = Gaps.gaps_with_dates(station)

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
    output_df.to_csv(f"predictions/{station}/Temp_{station}_aq.csv", index=False)
    #output_df.to_csv("temp_q.csv", index=False)

#TODO check if one neighbour too much missing data and ignore if necessary
def fill_aqn2gap(station, adj_list):

    cols = ["Flow"] #columns to check for missing data
    air_df = Read_txt.read_air_temp("air_temp")

    model_atq = Model(station, "atqn2wt", len(adj_list[station])+2)
    if station == -1:
        return -1

    #df_flow = pd.read_csv(f"filled_hydro\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")
    df_flow = pd.read_parquet(f"parquet_hydro\Flow/{station}_Abfluss_Tagesmittel.parquet")
    df_flow = df_flow.sort_values(by="Zeitstempel")
    df_temp = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
    df_temp = df_temp.sort_values(by="Zeitstempel")
    df_temp["Flow"] = df_flow["Wert"].to_numpy()
    for n in adj_list[station]:
        df_n = pd.read_csv(f"filled_hydro\Temp/{n}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        df_n = df_n.sort_values(by="Zeitstempel")
        df_temp[df_n["Stationsnummer"][0]] = df_n["Wert"].to_numpy()
        cols.append(df_n["Stationsnummer"][0])

    output_df = df_temp.set_index("Zeitstempel")
    missing_dates_df = Gaps.gaps_with_dates(station)

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

        #Check if one or more neighbours are missing and ignore them 
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
            value_list = Read_txt.get_air_betw(station, start, end, air_df, gap_l, big_adj)

            """ for n in adj_list[station]:
                if n not in missing_cols: """
            n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][n])
            
            
            value_wt = model_atq.aqn2gap(value_list, flow_list, n_list)
            array_value = value_wt.detach().numpy()
            output_df.loc[str(start): str(end_d-timedelta(days=1)),"Wert"] = array_value

    output_df.reset_index(inplace=True)
    output_df.to_csv(f"predictions/{station}/Temp_{station}_aqn.csv", index=False)
    #output_df.to_csv("temp_qn.csv", index=False)

def fill_aqn2gap_ignoring(station, adj_list):

    cols = ["Flow"] #columns to check for missing data
    air_df = Read_txt.read_air_temp("air_temp")

    model_atq = Model(station, "atqn2wt", len(adj_list[station])+2)
    if station == -1:
        return -1

    #df_flow = pd.read_csv(f"filled_hydro\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")
    df_flow = pd.read_parquet(f"parquet_hydro\Flow/{station}_Abfluss_Tagesmittel.parquet")
    df_flow = df_flow.sort_values(by="Zeitstempel")
    df_temp = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
    df_temp = df_temp.sort_values(by="Zeitstempel")
    df_temp["Flow"] = df_flow["Wert"].to_numpy()
    for n in adj_list[station]:
        df_n = pd.read_csv(f"filled_hydro\Temp/{n}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        df_n = df_n.sort_values(by="Zeitstempel")
        df_temp[df_n["Stationsnummer"][0]] = df_n["Wert"].to_numpy()
        cols.append(df_n["Stationsnummer"][0])

    output_df = df_temp.set_index("Zeitstempel")
    missing_dates_df = Gaps.gaps_with_dates(station)

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

        #Check if one or more neighbours are missing and ignore them 
        date_list = Gaps.consecutive_non_missing_with_neighbours(df_temp, str(start_date), str(end_date), cols)

        for start, end, missing_cols in date_list:
            if start == end:
                continue # All rows have some missing data
            start_d = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_d = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            gap_l = (end_d - start_d).days
            n_list = []
            flow_list = df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)]["Flow"]
            value_list = Read_txt.get_air_betw(station, start, end, air_df, gap_l, big_adj)

            for n in adj_list[station]:
                if n not in missing_cols:
                    n_list.append(df_temp[(df_temp["Zeitstempel"] >= start) & (df_temp["Zeitstempel"] < end)][n])
            
            
            value_wt = model_atq.aqn2gap(value_list, flow_list, n_list)
            array_value = value_wt.detach().numpy()
            output_df.loc[str(start): str(end_d-timedelta(days=1)),"Wert"] = array_value

    output_df.reset_index(inplace=True)
    output_df.to_csv(f"predictions/{station}/Temp_{station}_aqn.csv", index=False)
    
#returns the final estimation of the df
def return_final_df(station):
    df = pd.read_parquet(f"parquet_hydro\Temp\{station}_Wassertemperatur.parquet")
    df = df.sort_values(by="Zeitstempel")
    df = df.set_index("Zeitstempel")
    df_a = pd.read_csv(f"predictions\{station}\Temp_{station}_a.csv")
    df_a = df_a.sort_values(by="Zeitstempel")
    df_a = df_a.set_index("Zeitstempel")
    df_aq = pd.read_csv(f"predictions\{station}\Temp_{station}_aq.csv")
    df_aq = df_aq.sort_values(by="Zeitstempel")
    df_aq = df_aq.set_index("Zeitstempel")
    df_aqn = pd.read_csv(f"predictions\{station}\Temp_{station}_aqn.csv")
    df_aqn = df_aqn.sort_values(by="Zeitstempel")
    df_aqn = df_aqn.set_index("Zeitstempel")
    df["Model"] = "Source"

    df.loc[df["Wert"].isna(), "Model"] = "AQN2Gap"
    df["Wert"] = df["Wert"].fillna(df_aqn["Wert"])

    df.loc[df["Wert"].isna(), "Model"] = "AQ2Gap"
    df["Wert"] = df["Wert"].fillna(df_aq["Wert"])

    df.loc[df["Wert"].isna(), "Model"] = "A2Gap"
    df["Wert"] = df["Wert"].fillna(df_a["Wert"])

    df.reset_index(inplace=True)
    df.to_csv(f"predictions/{station}/Temp_final_{station}.csv", index=False)





if __name__ == "__main__":


    big_adj = Neighbour.all_adj_list()
    fill_aqn2gap(2288, big_adj)
       
    """ for st in os.listdir("models"):
        fill_a2gap(int(st), big_adj)
        fill_aq2gap(int(st), big_adj)
        fill_aqn2gap(int(st), big_adj) """
    
    for st in os.listdir("models"):
        return_final_df(int(st))
    
    #fill_aq2gap(2410, big_adj)
    #fill_a2gap(2481, big_adj)
    #fill_aq2gap(2481, big_adj)
    #fill_aqn2gap(2481, big_adj)
