import matplotlib.pyplot as plt
import pandas as pd
from txt_to_csv import Gaps, Read_txt
from neighbours import Neighbour
from my_graph_reader import ResourceRiverReaderFactory
from collections import Counter, defaultdict
import seaborn as sns
import missingno as msno
import os

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

#Plots length of each gap 
#column: column where missing values occur
def plot_missing_length(file_path, column):
    data = []
    files = os.listdir(file_path)
    for file in files:
        df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        df.sort_values(by="Zeitstempel", inplace=True)
        current_seq = 0

        for value in df[column].isnull():
            if value:
                current_seq+=1
            else:
                if(current_seq > 0):
                    data.append(current_seq)
                current_seq = 0
        if(current_seq > 0):
            data.append(current_seq)

    plt.hist(data, bins=40, rwidth=0.8, align="mid")
    plt.title("Amount of Gaps with given length")
    #plt.xticks(x)
    plt.show()

#plots a heatmap of all the missing values in the files of filepath
def plot_missing_values(file_path):
    data = []
    files = os.listdir(file_path)
    for file in files:
        df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        df_sorted = df.sort_values(by="Zeitstempel")
        data.append(df_sorted["Wert"])

    final_df = pd.DataFrame(data)
    
    plt.figure(figsize=(16, 8))
    msno.matrix(final_df)
    plt.show()

#Plots percentage of missing values per year
def plot_missing_per_year(file_path):
    data = []
    files = os.listdir(file_path)
    for file in files:
        df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'])
        data.append(df) 
    final_df = pd.concat(data, ignore_index=True) 

    final_df['Year'] = final_df['Zeitstempel'].dt.year
    missing_values = final_df['Wert'].isnull().groupby(final_df['Year']).mean()
    missing_values.plot(kind='bar', color='Grey')
    plt.title('Percentage of Missing Values in all Stations by Year')
    plt.xlabel('Year')
    plt.xticks(rotation=45)
    #plt.grid(axis='y')
    plt.show() 

#plots the amount of long gaps (>360) per year
#TODO maybe change to starting date again instead of for every year if it occurs
def plot_long_gaps(file_path):
    dates = []
    files = os.listdir(file_path)
    for file in files:
        df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        station = df["Stationsnummer"].iloc[0]
        station_df = Gaps.gaps_with_dates(station)   
        for index in station_df.index:
            if station_df["gap_length"][index] >= 360:
                start = station_df["start_date"][index].year
                end = station_df["end_date"][index].year
                date_range = range(start, end)
                for date in date_range:
                    dates.append(date)
    
    date_counts = Counter(dates)

    x = list(date_counts.keys())
    y = list(date_counts.values())
    plt.bar(x,y)
    plt.title('Amount of long Gaps (>360 days) per year')
    plt.xlabel('Year')
    plt.xticks(rotation=45)
    plt.show() 





if __name__=="__main__":

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    #plot_missing_neighbour_nr(adj_rhein)
    #plot_missing_length("filled_hydro\Temp", "Wert")
    #example = (Neighbour.get_Neighbour_values(2044, "1996-02-12 00:00:00", adj_rhein))
    #df = pd.read_csv(f"filled_hydro\Temp/2176_Wassertemperatur.txt", delimiter=';',  encoding="latin1")
    #df_sorted = df.sort_values(by="Zeitstempel")
    #msno.matrix(df_sorted)
    plot_long_gaps("filled_hydro/Temp")

