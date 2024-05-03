import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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
    mid_vals = [x for x in data if 20 < x <= 700]
    high_vals = [x for x in data if 700 < x]

    

    ax[0].hist(low_vals, bins=40, rwidth=0.8, align="mid")
    ax[0].set_title(r"Gap length $\leq$ 20")
    ax[0].set(ylabel = "Nr. of Occurences")
    ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax[1].hist(mid_vals, bins=40, rwidth=0.8, align="mid")

    ax[1].set_title(r"20 < Gap length $\leq$ 700")
    ax[2].hist(high_vals, bins=40, rwidth=0.8, align="mid")
    ax[2].set_title(r"Gap length > 700")
    
    

    
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

def plot_res_heatmeap():

    data = {}
    cols = ["Wert", "Model"]
    stations = os.listdir("predictions")
    for st in stations:
        df = pd.read_csv(f"predictions\{st}/Temp_final_{st}.csv", delimiter=",")
        df_sorted = df.sort_values(by="Zeitstempel")
        data[st] = df_sorted.set_index("Zeitstempel")["Model"]



    final_df = pd.DataFrame(data)
    #final_df = pd.concat(data, axis=0)
    final_df = final_df.sort_index()

    
    plt.figure(figsize=(18, 8))
    colors = ["grey", "cornflowerblue", "lightskyblue", "royalblue"]

    numbers = {
        "Source": 0,
        "A2Gap": 1,
        "AN2Gap": 2, #TODO Change it to AN2gap later on with return_final_df function renaming
        "AQN2Gap": 3
    }

    value_map = final_df.map(lambda x: numbers.get(x, -1))
    ax = sns.heatmap(value_map, cmap=colors)

    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.2, 2.0, 2.7])
    colorbar.set_ticklabels(["Source","A2Gap", "AQ2Gap","AQN2Gap"])


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

#Plots the value of two df into one plot
#df1 is a df from filled hydro and df2 the values from the filling main function
def plot_multi_color(df):
    # Convert Zeitpunkt_des_Auftretens column to datetime if it's not already
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'])
    
    # Filter timestamps after the year 2000
    df_filtered = df[df['Zeitstempel'].dt.year < 1987]
    
    # Separate data based on Freigabestatus
    df_red = df_filtered[df_filtered['Freigabestatus'] == 'hinzugefügte Daten']
    df_blue = df_filtered[df_filtered['Freigabestatus'] != 'hinzugefügte Daten']
    
    df_red_s = df_red.sort_values(by="Zeitstempel")
    df_blue_s = df_blue.sort_values(by="Zeitstempel")
    
    x_red = df_red_s["Zeitstempel"]
    y_red = df_red_s["Wert"]
    x_blue = df_blue_s["Zeitstempel"]
    y_blue = df_blue_s["Wert"]

    plt.plot(x_red, y_red, color="red", label="Imputed Data")
    plt.plot(x_blue, y_blue, color="blue", label="Recorded Data")
    plt.title("Water temperature of the station 2481")
    plt.ylabel("Temperature C°")
    plt.xlabel("Date")
    plt.legend()
    plt.show()



if __name__=="__main__":

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    #plot_missing_neighbour_nr(adj_rhein)
    #plot_missing_length("parquet_hydro\Temp", "Wert")
    #example = (Neighbour.get_Neighbour_values(2044, "1996-02-12 00:00:00", adj_rhein))
    
    plot_res_heatmeap()



