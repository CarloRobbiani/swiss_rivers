from my_graph_reader import ResourceRiverReaderFactory
import os
import pandas as pd
from txt_to_csv import Gaps

class Neighbour:
    
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
            if str(neighbour) == "-1":
                    continue
            #file_list = [path + f if str(neighbour) in f else "" for f in files]
            df = pd.read_csv(f"filled_hydro\Temp/{neighbour}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
            #df = pd.read_csv(file, delimiter=";", encoding="iso-8859-1")
            df.set_index('Zeitstempel', inplace=True)
            isMissing.append(int(pd.isna(df.loc[date, "Wert"])))

        return sum(isMissing)
    
    #Get the values of all neighbouring stations on a certain date
    def get_Neighbour_values(station, date, adj_list):
        values = {}
        neighbour_stations = Neighbour.get_neigbour(station, adj_list)
        for st in neighbour_stations:
            df = pd.read_csv(f"filled_hydro\Temp/{st}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
            df.set_index('Zeitstempel', inplace=True)
            values[st] = df.loc[date, "Wert"]
        return values


if __name__== "__main__":
    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    for station in adj_rhein:
        if str(station) == "-1":
                continue
        df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
        dates = Gaps.miss_date(df)
        n_list = Neighbour.get_neigbour(station, adj_rhein)
        for date in dates:
            miss = Neighbour.neighbour_missing(n_list, "filled_hydro/Temp", str(date))
            if miss > 0:
                 print(date, ": ",  miss)
    #print("Neighbours: ", get_neigbour(2143, adj_rhein))
