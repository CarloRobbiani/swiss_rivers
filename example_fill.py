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
from models import Models

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
                    output = Models.atqn2gap(air_low, air_high, air_target, discharge_low, discharge_high, discharge, 
                                      target_low, target_high, wt_n_low, wt_n_high, v_tens, station)
                    
                    print(f"Output: {output}")
                    output_df.loc[str(date), "Wert"] = output.item()

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
                            value_at = Models.a2gap(value, neighbour)
                            value_list.append(value_at)
                    #TODO use AQN2Gap model or AN2Gap model
                    output = Models.atqn2gap(air_low, air_high, air_target, discharge_low, discharge_high, discharge, 
                                      target_low, target_high, wt_n_low, wt_n_high, value_list, station)
                    
                    print(f"Output: {output}")
                    output_df.loc[str(date), "Wert"] = output.item()
                    """ new_row = {"Zeitstempel": date, "Wert" : output.item()}
                    dataframe = pd.concat([dataframe, pd.DataFrame([new_row])])
    df = pd.DataFrame(dataframe, columns=["Zeitstempel", "Wert"]) """
    output_df.reset_index(inplace=True)
    output_df.to_csv("temp.csv", index=False)


#fills in gaps only with air temperature
def fill_a2gap(station, adj_list):
    air_df = Read_txt.read_air_temp("air_temp")
    data = np.load("models/2481\Apr19_20-24-04_bnode051_11243919_1797_normalizers.npy")
    target_low, target_high = map(float, data[0][1:])
    discharge_low, discharge_high = map(float, data[1][1:])
    air_low, air_high = map(float, data[2][1:])
    wt_n_low, wt_n_high = map(float, data[3][1:])


    if station == -1:
        return -1

    #df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
    df = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
    df = df.sort_values(by="Zeitstempel")
    output_df = df.set_index("Zeitstempel")
    #df = pf.to_pandas()
    missing_dates_df = Gaps.gaps_with_dates(station)

    for index, row in missing_dates_df.iterrows():
        start_date = max((row["start_date"], datetime.strptime("1980-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")))
        end_date = row["end_date"]
        gap_length = row["gap_length"]
        date_range = pd.date_range(start_date + timedelta(days=1), end_date - timedelta(days=1))
        value_list = []
        
        value_list = Read_txt.get_air_betw(station, start_date, end_date, air_df)
            
        value_at = Models.a2gap(value_list, station)

        #output_df.loc[str(start_date): str(end_date)]["Wert"] = array_value
        output_df.reset_index(inplace=True)
        output_df.to_csv("temp.csv", index=False)


        




if __name__ == "__main__":


    big_adj = Neighbour.all_adj_list()
    fill_a2gap(2481, big_adj)