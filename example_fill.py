from neighbours import Neighbour
import os
import pandas as pd
from txt_to_csv import Gaps, Read_txt
from datetime import datetime, timedelta
from hydro_to_meteo import Hydro2MeteoMapper
from my_graph_reader import ResourceRiverReaderFactory
import profile
from line_profiler import LineProfiler
from fastparquet import ParquetFile
from normalizer import MinMaxNormalizer
from prediction import RecurrentPredictionModel
import json
import torch
import numpy as np
from filling_main import interpolate, fill_with_air, return_flow, isnewer

def fill(station, adj_list):
    #temporary df for presentation
    d = {"Zeistempel": ["0000"], "Wert":[None]}
    dataframe = pd.DataFrame(d)

    print(f"Station {station}")

    data = np.load("models/2170\Apr19_15-58-07_bnode051_11234070_2823_normalizers.npy")
    target_low, target_high = map(float, data[0][1:])
    discharge_low, discharge_high = map(float, data[1][1:])
    air_low, air_high = map(float, data[2][1:])
    wt_n_low, wt_n_high = map(float, data[3][1:])


    if station == -1:
        return -1

    #df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
    df = pd.read_parquet(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
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
                new_row = {"Zeitstempel": date, "Wert" : out}
                dataframe = pd.concat([dataframe, pd.DataFrame([new_row])])
            
        else:
            #TODO use either air temperature or neighbour + discharge
            neighbour_list = adj_list[station]
            length = len(neighbour_list)

            #TODO make it faster
            for date in date_range:
                value_list = []
                missing_nr = Neighbour.neighbour_missing(neighbour_list, str(date))
                discharge = return_flow(station, date)
                air_target = fill_with_air(station, date, adj_list)

                #case no missing neighbours
                if missing_nr == 0:
                    values = Neighbour.get_Neighbour_values(station, str(date), adj_list)
                    print("No missing Neighbours")
                    #TODO use either AQN2gap or AN2gap
                    output = atqn2gap(air_low, air_high, air_target, discharge_low, discharge_high, discharge, 
                                      target_low, target_high, wt_n_low, wt_n_high, values)
                    
                    print(f"Output: {output}")
                    new_row = {"Zeitstempel": date, "Wert" : output.item()}
                    dataframe = pd.concat([dataframe, pd.DataFrame([new_row])])

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
                            value_at = a2gap(air_low, air_high, value, target_low, target_high)
                            value_list.append(value_at)
                    #TODO use AQN2Gap model or AN2Gap model
                    output = atqn2gap(air_low, air_high, air_target, discharge_low, discharge_high, discharge, 
                                      target_low, target_high, wt_n_low, wt_n_high, value_list)
                    
                    print(f"Output: {output}")
                    new_row = {"Zeitstempel": date, "Wert" : output.item()}
                    dataframe = pd.concat([dataframe, pd.DataFrame([new_row])])
    df = pd.DataFrame(dataframe, columns=["Zeitstempel", "Wert"])
    df.to_csv("temp.csv", index=False)


def a2gap(air_low, air_high, air_t, t_low, t_high):
    air_temp = np.array([air_low, air_high])
    target = np.array([t_low, t_high])
    norm_t = MinMaxNormalizer(target)
    normalizer_air = MinMaxNormalizer(air_temp)
    n_at = float(normalizer_air.normalize(air_t))

    f = open('C:/Users\carlo\OneDrive\Documents\GitHub\swiss_rivers\models/2170/2170_at2wt_T1990_metadata.json')

    metadata = json.load(f)
    print(metadata["hyperparameters"])

    model = RecurrentPredictionModel(1, 
                                     int(metadata["hyperparameters"]["width"]),
                                     int(metadata["hyperparameters"]["depth"]),)
    
    model.load_state_dict(torch.load("models/2170\Apr18_15-56-57_bnode029_11183649_2787_best_valid_loss_at2wt.pt"))

    input_data = torch.tensor([[n_at]])
    output = model.forward(input_data) 
    #print(output)
    norm_output = norm_t.denormalize(output)
    print(norm_output)
    return norm_output

#TODO Turn n_t list into a tensor?
def atqn2gap(air_low, air_high, air_t, q_low, q_high, q_target, t_low, t_high, n_low, n_high, n_t):
    air_temp = np.array([air_low, air_high])
    discharge = np.array([q_low, q_high])
    nei = np.array([n_low, n_high])
    target = np.array([t_low, t_high])
    norm_targ = MinMaxNormalizer(target)
    normalizer_air = MinMaxNormalizer(air_temp)
    normalizer_d = MinMaxNormalizer(discharge)
    normalizer_n = MinMaxNormalizer(nei)
    n_at = float(normalizer_air.normalize(air_t))
    n_q = float(normalizer_d.normalize(q_target))
    n_nei = float(normalizer_n.normalize(n_t[0].item()))

    f = open("C:/Users\carlo\OneDrive\Documents\GitHub\swiss_rivers\models/2170/2170_atqn2wt_T1990_N2174_metadata.json")
    metadata = json.load(f)
    model = RecurrentPredictionModel(3, 
                                     int(metadata["hyperparameters"]["width"]),
                                     int(metadata["hyperparameters"]["depth"]),)
    
    model.load_state_dict(torch.load("models/2170\Apr18_16-58-54_bnode028_11185597_2859_best_valid_loss_atqn2wt.pt"))
    input_data = torch.tensor([[n_at,n_q,n_nei]])
    output = model.forward(input_data) 
    #print(output)
    norm_out = norm_targ.denormalize(output)
    print(norm_out)
    return norm_out

def atn2gap(air_low, air_high, air_t, t_low, t_high, n_low, n_high, n_t):
    air_temp = np.array([air_low, air_high])

    nei = np.array([n_low, n_high])
    target = np.array([t_low, t_high])
    norm_targ = MinMaxNormalizer(target)
    normalizer_air = MinMaxNormalizer(air_temp)
    normalizer_n = MinMaxNormalizer(nei)
    n_at = normalizer_air.normalize(air_t)

    n_nei = normalizer_n.normalize(n_t[0].item())

    f = open("C:/Users\carlo\OneDrive\Documents\GitHub\swiss_rivers\models/2170/2170_atq2wt_T1990_metadata.json")
    metadata = json.load(f)
    model = RecurrentPredictionModel(2, 
                                     int(metadata["hyperparameters"]["width"]),
                                     int(metadata["hyperparameters"]["depth"]),)
    
    model.load_state_dict(torch.load("models/2170\Apr19_15-58-07_bnode051_11234070_2823_best_valid_loss_atq2wt.pt"))
    input_data = torch.tensor([[n_at,n_nei]])
    output = model.forward(input_data) 
    #print(output)
    norm_out = norm_targ.denormalize(output)
    print(norm_out)
    return norm_out

if __name__ == "__main__":
    big_adj = Neighbour.all_adj_list()
    fill(2170, big_adj)