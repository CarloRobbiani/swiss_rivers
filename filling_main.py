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
import numpy as np
from models import Model

#takes a station and a date in the date format and returns the air temp of that station and date
#TODO check if its an empty dataframe and take a year later otherwise  
def fill_with_air(station, date, adj_list, air_df):

    #dt_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    dt = date.strftime("%Y%m%d")

    h2m = Hydro2MeteoMapper()

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

#Function that takes a station and a date and returns the flow (-1 if its missing)
#Takes in a station number as int and date in the format of "1980-01-10 00:00:00"
def return_flow(station, date):

    flow_df = pd.read_csv(f"filled_hydro\Flow/{station}_Abfluss_Tagesmittel.txt", delimiter=';',  encoding="latin1")

    row = flow_df.loc[(flow_df['Stationsnummer'] == station) & (flow_df['Zeitstempel'] == str(date))]

    if pd.isna(row["Wert"].iloc[0]):
        return -1

    return row["Wert"].iloc[0]

def interpolate(df, start_date, end_date):
   start_value = df.loc[df["Zeitstempel"] == str(start_date), "Wert"].iloc[0]
   end_value = df.loc[df["Zeitstempel"] == str(end_date), "Wert"].iloc[0]

   result = float((start_value + end_value) / 2)
   return result

#Takes a station and returns True if it was built after the specified date
def isnewer(station, date):
    df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")

    building_date = df["Zeitstempel"].iloc[0]
    building_year = int(building_date[:4])
    spec_date = int(date[:4])
    if building_year > spec_date:
        return True
    return False
    



if __name__ == "__main__":

    big_adj = Neighbour.all_adj_list()
    #date = datetime.strptime("1971-05-11 00:00:00", "%Y-%m-%d %H:%M:%S")

    #print(fill_with_air(2457,date, big_adj))

    #print(return_flow(2609, "1988-09-18 00:00:00"))

    #profile(fill(data_x_rhein, data_edges_rhein, adj_rhein))
    #print_stats()

