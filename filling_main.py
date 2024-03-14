from neighbours import Neighbour
import os
import pandas as pd
from txt_to_csv import Gaps
import datetime

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
                


