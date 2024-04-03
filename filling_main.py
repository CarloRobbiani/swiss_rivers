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


profiler = LineProfiler()

def profile(func):
    def inner(*args, **kwargs):
        profiler.add_function(func)
        profiler.enable_by_count()
        return func(*args, **kwargs)
    return inner

def print_stats():
    profiler.print_stats()

#function that takes a station (int) and a adj list and fills the missing values with the models
#@profile
def fill(station, adj_list):

    print(f"Station {station}")

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
                value = interpolate(df, start_date, end_date)
                print(value)
            
        else:
            #TODO use either air temperature or neighbour + discharge
            neighbour_list = adj_list[station]
            length = len(neighbour_list)

            #TODO make it faster
            for date in date_range:
                missing_nr = Neighbour.neighbour_missing(neighbour_list, str(date))
                discharge = return_flow(station, date)

                #case no missing neighbours
                if missing_nr == 0:
                    value_list = Neighbour.get_Neighbour_values(station, str(date), adj_list)
                    print("No missing Neighbours")

                #case some missing neighbours
                elif length > missing_nr > 0:
                    for neighbour in neighbour_list:
                        gap_len = Gaps.find_gap_length(neighbour, str(date))
                        if 0 < gap_len <=2:
                            #interpolate
                            #df_n =  pd.read_csv(f"filled_hydro\Temp/{neighbour}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
                            pf = ParquetFile(f"parquet_hydro\Temp/{neighbour}_Wassertemperatur.parquet")
                            df_n = pf.to_pandas()
                            value = interpolate(df_n, start_date, end_date)
                            print(f"Neighbour {neighbour} temp: {value}")

                        #TODO else ignore

                #case only missing neighbours
                elif missing_nr == length:
                    #use air temperature
                    result = fill_with_air(station, date, adj_list)
                    #print(f"Air: {result}")
                    continue


#takes a station and a date in the date format and returns the air temp of that station and date
#TODO check if its an empty dataframe and take a year later otherwise
#TODO convert date from "1980-01-10 00:00:00" to 19800101        
def fill_with_air(station, date, adj_list):

    #dt_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


    dt = date.strftime("%Y%m%d")


    h2m = Hydro2MeteoMapper()
    air_df = Read_txt.read_air_temp("air_temp")

    air_station = (h2m.meteo(str(station)))
    row = air_df.loc[(air_df['stn'] == air_station) & (air_df['time'] == int(dt))]
    #if we encounter a missing value take value from a neighbour
    #TODO maybe change  it to neighbouring station of air station
    if row["tre200d0"].iloc[0] == "-":
        neighbour = adj_list[station][0]
        n_station = (h2m.meteo(str(neighbour)))
        row = air_df.loc[(air_df['stn'] == n_station) & (air_df['time'] == int(dt))]
        return row["tre200d0"].iloc[0]
    return row["tre200d0"].iloc[0]

    #print(hydro_stations)

#Function that takes a station and a date and returns the flow
#Takes in a station number as int and date in the format of "1980-01-10 00:00:00"
def return_flow(station, date):

    flow_df = pd.read_csv(f"filled_hydro\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")

    row = flow_df.loc[(flow_df['Stationsnummer'] == station) & (flow_df['Zeitstempel'] == date)]

    if pd.isna(row["Wert"].iloc[0]):
        return -1

    return row["Wert"].iloc[0]

def interpolate(df, start_date, end_date):
   start_value = df.loc[df["Zeitstempel"] == str(start_date), "Wert"].iloc[0]
   end_value = df.loc[df["Zeitstempel"] == str(end_date), "Wert"].iloc[0]

   result = float((start_value + end_value) / 2)
   return result


if __name__ == "__main__":

    big_adj = Neighbour.all_adj_list()
    #date = datetime.strptime("1971-05-11 00:00:00", "%Y-%m-%d %H:%M:%S")

    #print(fill_with_air(2457,date, big_adj))

    #print(return_flow(2609, "1988-09-18 00:00:00"))



    fill(2327, big_adj)
    

    #profile(fill(data_x_rhein, data_edges_rhein, adj_rhein))
    #print_stats()

