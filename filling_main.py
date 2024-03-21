from neighbours import Neighbour
import os
import pandas as pd
from txt_to_csv import Gaps, Read_txt
import datetime
from hydro_to_meteo import Hydro2MeteoMapper

#function that takes the river data and fills the missing values with the models
def fill(data_x, data_edges, adj_list):
    for station in adj_list:

        df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
        missing_dates_df = Gaps.miss_date(df)

        for start_date, value in missing_dates_df["gap_length"].items():
            end_date = missing_dates_df["end_date"].loc["start_date"] + datetime.timedelta(days=1)
            date_range = range(start_date, end_date)
            if value < 3:
                #TODO use interpolation
                for date in date_range:
                    continue
                continue
            else:
                #TODO use either air temperature or neighbour
                neighbour_list = Neighbour.get_neigbour(station, adj_list)
                length = len(neighbour_list)
                for date in date_range:
                    missing_nr = Neighbour.neighbour_missing(neighbour_list, "filled_hydro/Temp", date)

                    #case no missing neighbours
                    if missing_nr == 0:
                        value_list = Neighbour.get_Neighbour_values(station, date, adj_list)
                    #case some missing neighbours
                    if missing_nr > 0:
                        for neighbour in neighbour_list:
                            gap_length = Gaps.find_gap_length(neighbour, date)
                            if gap_length <=2:
                                #interpolate
                                continue 
                    #case only much missing neighbours
                    if missing_nr == length:
                        #TODO use air temperature
                        continue
                continue

#takes a station and a date in the fromat YYYYMMDD and returns the air temp of that station and date
#TODO check if its an empty dataframe and take a year later otherwise
#TODO what meteo mapper to take?
#TODO convert date from "1980-01-10 00:00:00" to 19800101        
def fill_with_air(station, date, adj_list):
    h2m = Hydro2MeteoMapper()
    air_df = Read_txt.read_air_temp("air_temp")

    air_station = (h2m.meteo(str(station)))
    row = air_df.loc[(air_df['stn'] == air_station) & (air_df['time'] == date)]
    #if we encounter a missing value take value from a neighbour
    #maybe change  it to neighbouring station
    if row["tre200d0"].iloc[0] == "-":
        neighbour = adj_list[station][0]
        row = air_df.loc[(air_df['stn'] == neighbour) & (air_df['time'] == date)]
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

if __name__ == "__main__":
    print(fill_with_air(2457, 19710511))

    print(return_flow(2609, "1988-09-18 00:00:00"))

