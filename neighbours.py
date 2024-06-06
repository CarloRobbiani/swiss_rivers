from my_graph_reader import ResourceRiverReaderFactory
import pandas as pd
from txt_to_csv import Gaps
from fastparquet import ParquetFile
import numpy as np

class Neighbour:

    #station lookup table for the special cases returns 0 if station not in list
    #TODO check if both directions are needed
    def alter_neighbour(station):
        adj_list = {
            2179 : 2085,
            2308 : 2143,
            2033 : 2143,
            2126 : 2044,
            2410 : 2143,
            2150 : 2143,
            2327 : 2143,
            2432 : 2174,
            2617 : 2462,
            2167 : 2068,
            2612 : 2068,
            2109 : 2030,
            2019 : 2030,
            2473 : 2143,
            2009 : 2174
        }
        if station not in adj_list:
            return 0

        return adj_list.get(station)


    
    #Enter a data tensor and its edges and create an adjacency list.
    def get_adj(data, edges):
        adj_list = {}
        for i in range(edges.shape[1]):
            start = data[edges[0,i], 2].item()
            end = data[edges[1,i], 2].item()
            if start == -1 or end == -1:
                continue
            if start not in adj_list:
                adj_list[start] = []
            adj_list[start].append(end)
            if end not in adj_list:
                adj_list[end] = []
            adj_list[end].append(start)
        return adj_list
    
    def all_adj_list():
        big_adj = {}

        reader_rhein = ResourceRiverReaderFactory.rhein_reader(-2010)
        data_x_rhein, data_edges_rhein = reader_rhein.read()
        adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
        big_adj.update(adj_rhein)

        reader_inn = ResourceRiverReaderFactory.inn_reader()
        data_x_inn, data_edges_inn = reader_inn.read()
        adj_inn = Neighbour.get_adj(data_x_inn, data_edges_inn)
        big_adj.update(adj_inn)

        reader_rohne = ResourceRiverReaderFactory.rohne_reader(-2010)
        data_x_rohne, data_edges_rohne = reader_rohne.read()
        adj_rohne = Neighbour.get_adj(data_x_rohne, data_edges_rohne)
        big_adj.update(adj_rohne)

        reader_ti = ResourceRiverReaderFactory.ticino_reader()
        data_x_ti, data_edges_ti = reader_ti.read()
        adj_ti = Neighbour.get_adj(data_x_ti, data_edges_ti)
        big_adj.update(adj_ti)

        return big_adj


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
    def neighbour_missing(neighbour_list, date):
        isMissing = []
        for neighbour in neighbour_list:
            if neighbour == -1:
                    continue
            #df = pd.read_csv(f"filled_hydro\Temp/{neighbour}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
            df = pd.read_parquet(f"parquet_hydro\Temp/{neighbour}_Wassertemperatur.parquet")
            #df = pf.to_pandas()
            df.set_index('Zeitstempel', inplace=True)
            isMissing.append(int(pd.isna(df.loc[date, "Wert"])))

        return sum(isMissing)
    
    #Get the values of all neighbouring stations on a certain date
    def get_Neighbour_values(station, date, adj_list):
        values = {}
        neighbour_stations = Neighbour.get_neigbour(station, adj_list)
        for st in neighbour_stations:
            if st == -1:
                continue

            #df = pd.read_csv(f"filled_hydro\Temp/{st}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
            pf = ParquetFile(f"parquet_hydro\Temp/{st}_Wassertemperatur.parquet")
            df = pf.to_pandas()
            df.set_index('Zeitstempel', inplace=True)
            values[st] = df.loc[date, "Wert"]
        return values
    
    #returns the value of a station on a given date
    def get_value(station, date):
        pf = ParquetFile(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        df = pf.to_pandas()

        value = station.loc[station["Zeitstempel"] == date]["Wert"]
        if value == np.nan:
            return None
        return value


if __name__== "__main__":
    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-2010)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    for station in adj_rhein:
        if str(station) == "-1":
                continue
        #df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
        pf = ParquetFile(f"parquet_hydro\Temp/{station}_Wassertemperatur.parquet")
        df = pf.to_pandas()
        dates = Gaps.miss_date(df)
        n_list = Neighbour.get_neigbour(station, adj_rhein)
        for date in dates:
            miss = Neighbour.neighbour_missing(n_list, str(date))
            if miss > 0:
                 print(date, ": ",  miss)
    #print("Neighbours: ", get_neigbour(2143, adj_rhein))
