from my_graph_reader import ResourceRiverReaderFactory
import os
import pandas as pd
from txt_to_csv import find_missing_dates

#Enter a data tensor and its edges and create an adjacency list.
def get_adj(data, edges):
    adj_list = {}
    for i in range(edges.shape[1]):
        start = data[edges[0,i], 2].item()
        end = data[edges[1,i], 2].item()
        if start not in adj_list:
            adj_list[start] = []
        adj_list[start].append(end)
        if end not in adj_list:
            adj_list[end] = []
        adj_list[end].append(start)
    return adj_list


#Enter station_nr and adjacency list from the river in hydro data and return the neighbouring stations
#Problem: find right adj list
#station: station number ####
def get_neigbour(station, adj_list):
    if station not in adj_list:
        return []
    return adj_list[station]

#Method to get if neigbours of a station have missing values. Returns number of missing values
#neighbour list: result of get_neighbour function
#path: path where .txt files are stored
#date: the date where we found missing values in data
def neighbour_missing(neighbour_list, path, date):
    isMissing = []
    files = os.listdir(path)
    for neighbour in neighbour_list:
        file_list = [path + f if neighbour in f else "" for f in files]
    for file in file_list:
        df = pd.read_csv(file, delimiter=";", encoding="iso-8859-1")
        df.set_index('Zeitstempel', inplace=True)
        isMissing.append(int(pd.isna(df.loc[date, "Wert"])))

    return sum(isMissing)


if __name__== "__main__":
    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = get_adj(data_x_rhein, data_edges_rhein)
    n_list = get_neigbour(2143, adj_rhein)
    df = pd.read_csv("filled_hydro\Temp/2143_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
    dates = find_missing_dates(df)
    for date in dates:
        miss = neighbour_missing(n_list, "filled_hydro/Temp", )
        print(miss)
    print("Neighbours: ", get_neigbour(2143, adj_rhein))
