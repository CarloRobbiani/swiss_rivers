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
    fig, ax = plt.subplots(1,3)

    data = []
    files = os.listdir(file_path)
    for file in files:
        #df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        df = pd.read_parquet(f"parquet_hydro\Temp/{file}")
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

    low_vals = [x for x in data if x <= 20]
    mid_vals = [x for x in data if 20 < x <= 365]
    high_vals = [x for x in data if 365 < x]

    

    ax[0].hist(low_vals, bins=40, rwidth=0.8, align="mid")
    ax[0].set_title(r"Gap length $\leq$ 20")
    ax[0].set(ylabel = "Nr. of Occurences")
    ax[1].hist(mid_vals, bins=40, rwidth=0.8, align="mid")

    ax[1].set_title(r"20 < Gap length $\leq$ 100")
    ax[2].hist(high_vals, bins=40, rwidth=0.8, align="mid")
    ax[2].set_title(r"Gap length $\geq$ 365")
    
    

    
    for axs in ax.flat:
        axs.set(xlabel='Days')

    fig.suptitle("Amount of Gaps in Water temp. with given length")
    plt.show()

#plots a heatmap of all the missing values in the files of filepath
#TODO Annotate plot with station numbers and years and so on
def plot_missing_values(file_path):
    data = {}
    files = os.listdir(file_path)
    for file in files:
        df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        df_sorted = df.sort_values(by="Zeitstempel")

        station = df_sorted.iloc[0,1]
        data[station] = df_sorted.set_index("Zeitstempel")["Wert"]



    final_df = pd.DataFrame(data)
    final_df = final_df.sort_index()

    
    plt.figure(figsize=(18, 8))
    colours = ["grey", "lightgray"] 
    ax = sns.heatmap(final_df.isnull(), cmap=colours)

    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.25,0.75])
    colorbar.set_ticklabels(['Not missing', 'missing'])


    plt.yticks(rotation=0) 
    plt.yticks(range(0, len(final_df.index), 700), [x[:4] for x in final_df.index[::700]]) 
    plt.title("Missing values per station and year")
    plt.ylabel("Time")
    plt.xlabel("Station")
   

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
    dates_short = []
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

            if station_df["gap_length"][index] <= 2:
                start = station_df["start_date"][index].year
                end = station_df["end_date"][index].year
                #date_range = range(start, end)
                dates_short.append(start)
    
    date_counts = Counter(dates)
    date_short_counts = Counter(dates_short)

    x = sorted(list(date_counts.keys()))
    y = list(date_counts.values())
    x_short = sorted(list(date_short_counts.keys()))
    y_short = list(date_short_counts.values())
    plt.plot(x,y, label = "long gaps", marker = "o")
    plt.plot(x_short, y_short, label = "short gaps", marker = "o")
    plt.title('Amount of long Gaps (>360 days) per year')
    plt.xlabel('Year')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show() 





if __name__=="__main__":

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    #plot_missing_neighbour_nr(adj_rhein)
    #plot_missing_length("parquet_hydro\Temp", "Wert")
    #example = (Neighbour.get_Neighbour_values(2044, "1996-02-12 00:00:00", adj_rhein))

    #plot_long_gaps("filled_hydro/Temp")
    plot_missing_values("filled_hydro\Temp")
    #plot_missing_per_year("filled_hydro/Temp")

