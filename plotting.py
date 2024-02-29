import matplotlib.pyplot as plt
import pandas as pd
from txt_to_csv import Gaps
from neighbours import Neighbour
from my_graph_reader import ResourceRiverReaderFactory
from collections import Counter

#plots the nr of missing values of neighbours as a bar plot
def plot_missing_neighbour_nr(adj_list):
    values = []
    for station in adj_list:
        if str(station) == "-1":
            continue
        df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
        dates = Gaps.miss_date(df)
        n_list = Neighbour.get_neigbour(station, adj_list)
        for date in dates:
            miss = Neighbour.neighbour_missing(n_list, "filled_hydro/Temp", str(date))
            values.append(miss)
    
    value_counts = Counter(values)

    x = list(value_counts.keys())
    y = list(value_counts.values())
    plt.bar(x,y)
    plt.xticks(x)
    plt.show()

def plot_missing_length(station_nr, column):

    df = pd.read_csv(f"filled_hydro\Temp/{station_nr}_Wassertemperatur.txt", delimiter=';',  encoding="iso-8859-1")
    missing_list = Gaps.missing_len(df, column, False)
    x = list(missing_list.keys())
    y = list(missing_list.values())
    
    plt.bar(x, y)
    plt.xticks(x)
    plt.show()

if __name__=="__main__":

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    #plot_missing_neighbour_nr(adj_rhein)
    #plot_missing_length(2091, "Wert")
    example = (Neighbour.get_Neighbour_values(2044, "1996-02-12 00:00:00", adj_rhein))
        