import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
from txt_to_csv import Gaps, Read_txt
from neighbours import Neighbour
from graph_reader import ResourceRiverReaderFactory
from collections import Counter, defaultdict
import seaborn as sns
import os
import matplotlib.lines as mlines
import numpy as np
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
        df = pd.read_csv(f"filled_hydro\Temp/{file}", delimiter=';',  encoding="latin1")
        #df = pd.read_parquet(f"parquet_hydro\Temp/{file}")
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

#plots heatmap with colours depending on model
#TODO consider special cases, same category as AQN2Gap
def plot_res_heatmeap():

    data = {}
    stations = os.listdir("predictions")
    for st in stations:
        df = pd.read_csv(f"predictions\{st}/Temp_final_{st}.csv", delimiter=",")
        df_sorted = df.sort_values(by="Zeitstempel")
        data[st] = df_sorted.set_index("Zeitstempel")["Model"]



    final_df = pd.DataFrame(data)
    final_df.replace("AQN2Gap_special", "AQN2Gap", inplace=True) #such that the special cases also count in for the AQN2Gap model
    #final_df = pd.concat(data, axis=0)
    final_df = final_df.sort_index()

    
    plt.figure(figsize=(18, 8))
    colors = ["grey","paleturquoise", "cornflowerblue", "mediumblue"]

    numbers = {
        "Source": 0,
        "A2Gap": 1,
        "AQ2Gap": 2,
        "AQN2Gap": 3
    }

    value_map = final_df.map(lambda x: numbers.get(x, -1))
    ax = sns.heatmap(value_map, cmap=colors)

    colorbar = ax.collections[0].colorbar
    colorbar.set_ticks([0.4, 1.1, 1.9, 2.6])
    colorbar.set_ticklabels(["Source","A2Gap", "AQ2Gap","AQN2Gap"])


    plt.yticks(rotation=0) 
    plt.yticks(range(0, len(final_df.index), 700), [x[:4] for x in final_df.index[::700]]) 
    plt.title("Models used for imputing gaps")
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

#Plots gaps of df
#df is a  df from the predictions
def plot_multi_color(df):
    
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'])
    
    # Filter timestamps 
    df_filtered = df[df['Zeitstempel'].dt.year < 1990]
    df_filtered = df_filtered[df_filtered["Zeitstempel"].dt.year > 1980]

    df_filtered = df_filtered.sort_values(by="Zeitstempel")
    

    color_map = {'hinzugefÃ¼gte Daten': 'red', 'other': 'blue'}
    colors = df_filtered['Freigabestatus'].map(lambda x: color_map.get(x, 'blue'))
    
    x = df_filtered['Zeitstempel']
    y = df_filtered['Wert']

    fig, ax = plt.subplots()
    for i in range(len(x) - 1):
        ax.plot(x.iloc[i:i+2], y.iloc[i:i+2], color=colors.iloc[i])

    red_line = mlines.Line2D([], [], color='red', label='Imputed Data')
    blue_line = mlines.Line2D([], [], color='blue', label='Recorded Data')
    ax.legend(handles=[red_line, blue_line])
    plt.title("Water temperature of the station 2288")
    plt.ylabel("Temperature C°")
    plt.xlabel("Date")
    plt.show()

#Plots the different model results into one plot
def plot_overlapping(station):
    folder = f"predictions/{station}"

    a2gap = pd.read_csv(f"{folder}/Temp_{station}_a.csv")
    aq2gap = pd.read_csv(f"{folder}/Temp_{station}_aq.csv")
    aqn2gap = pd.read_csv(f"{folder}/Temp_{station}_aqn.csv")
    interpolation = pd.read_csv(f"{folder}/Temp_{station}_interpolation.csv")

    a_x,a_y,a_colors = read_df_with_colors(a2gap, "red")
    aq_x,aq_y,aq_colors = read_df_with_colors(aq2gap, "orange")
    aqn_x,aqn_y,aqn_colors = read_df_with_colors(aqn2gap, "green")
    i_x,i_y,i_colors = read_df_with_colors(interpolation, "black")

    fig, ax = plt.subplots()
    for i in range(len(a_x) - 1):
        ax.plot(a_x.iloc[i:i+2],a_y.iloc[i:i+2], color = a_colors.iloc[i])
        ax.plot(aq_x.iloc[i:i+2],aq_y.iloc[i:i+2], color = aq_colors.iloc[i], linestyle = "dotted")
        ax.plot(aqn_x.iloc[i:i+2],aqn_y.iloc[i:i+2], color = aqn_colors.iloc[i], linestyle = "dashed")
        ax.plot(i_x.iloc[i:i+2],i_y.iloc[i:i+2], color = i_colors.iloc[i])

    red_line = mlines.Line2D([], [], color='red', label='A2Gap')
    yellow_line = mlines.Line2D([], [], color='orange', label='AQ2Gap', linestyle=":")
    green_line = mlines.Line2D([], [], color='green', label='AQN2Gap', linestyle="--")
    blue_line = mlines.Line2D([], [], color='blue', label='Recorded Data')
    black_line = mlines.Line2D([], [], color='black', label='Interpolation')
    ax.legend(handles=[red_line, yellow_line, green_line, blue_line, black_line])
    plt.title(f"Water temperature of the station {station}")
    plt.ylabel("Temperature C°")
    plt.xlabel("Date")
    plt.show()


def plot_artificial_gap(station):
    folder = f"predictions/{station}"

    original = pd.read_csv(f"filled_hydro/Temp/{station}_Wassertemperatur copy.txt", delimiter=";")

    a2gap = pd.read_csv(f"{folder}/Temp_{station}_a.csv")
    aq2gap = pd.read_csv(f"{folder}/Temp_{station}_aq.csv")
    aqn2gap = pd.read_csv(f"{folder}/Temp_{station}_aqn.csv")
    interpolation = pd.read_csv(f"{folder}/Temp_{station}_interpolation.csv")

    o_x, o_y, o_colors = read_df_with_colors(original, "blue")
    a_x,a_y,a_colors = read_df_with_colors(a2gap, "red")
    aq_x,aq_y,aq_colors = read_df_with_colors(aq2gap, "orange")
    aqn_x,aqn_y,aqn_colors = read_df_with_colors(aqn2gap, "green")
    i_x, i_y, i_colors = read_df_with_colors(interpolation, "darkgreen")

    fig, ax = plt.subplots()
    for i in range(len(a_x) - 1):
        ax.plot(o_x.iloc[i:i+2],o_y.iloc[i:i+2], color = o_colors.iloc[i])
        ax.plot(a_x.iloc[i:i+2],a_y.iloc[i:i+2], color = a_colors.iloc[i])
        ax.plot(aq_x.iloc[i:i+2],aq_y.iloc[i:i+2], color = aq_colors.iloc[i], linestyle = "dotted")
        ax.plot(aqn_x.iloc[i:i+2],aqn_y.iloc[i:i+2], color = aqn_colors.iloc[i], linestyle = "dashed")
        ax.plot(i_x.iloc[i:i+2],i_y.iloc[i:i+2], color = i_colors.iloc[i])

    red_line = mlines.Line2D([], [], color='red', label='A2Gap')
    yellow_line = mlines.Line2D([], [], color='orange', label='AQ2Gap', linestyle=":")
    green_line = mlines.Line2D([], [], color='green', label='AQN2Gap', linestyle="--")
    blue_line = mlines.Line2D([], [], color='blue', label='Recorded Data')
    dark_green_line = mlines.Line2D([], [], color='darkgreen', label='Interpolation')
    ax.legend(handles=[red_line, yellow_line, green_line, blue_line, dark_green_line])
    plt.title(f"Water temperature of the station {station}")
    plt.ylabel("Temperature C°")
    plt.xlabel("Date")
    plt.show()

    
#helper function for coloring and filtering
def read_df_with_colors(df, impute_color):


    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'])
    df["Freigabestatus"] = np.where(df["Wert"].apply(has_more_than_5_decimals), 'hinzugefÃ¼gte Daten', df["Freigabestatus"])
    
    # Filter timestamps 
    df_filtered = df[df['Zeitstempel'].dt.year < 2020]
    df_filtered = df_filtered[df_filtered["Zeitstempel"].dt.year > 2016]

    df_filtered = df_filtered.sort_values(by="Zeitstempel")
    

    #color_map = {'hinzugefÃ¼gte Daten': impute_color, 'other': 'blue'}
    color_map = {'hinzugefÃ¼gte Daten': impute_color, 'other': 'blue'}
    colors = df_filtered['Freigabestatus'].map(lambda x: color_map.get(x, 'blue'))
    
    x = df_filtered['Zeitstempel']
    y = df_filtered['Wert']
    return x,y,colors

def has_more_than_5_decimals(value):
    return len(str(value).split('.')[1]) > 5 if '.' in str(value) else False

#check if a station was already built on a specific day or not
def isnewer(station, date):
    df = pd.read_csv(f"filled_hydro\Temp/{station}_Wassertemperatur.txt", delimiter=';',  encoding="latin1")

    building_date = df["Zeitstempel"].iloc[0]
    building_year = int(building_date[:4])
    spec_date = int(date[:4])
    if building_year > spec_date:
        return True
    return False

if __name__=="__main__":

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = Neighbour.get_adj(data_x_rhein, data_edges_rhein)
    #plot_missing_neighbour_nr(adj_rhein)
    #plot_missing_length("parquet_hydro\Temp", "Wert")
    #example = (Neighbour.get_Neighbour_values(2044, "1996-02-12 00:00:00", adj_rhein))

    #df = pd.read_csv("predictions/2608\Temp_final_2608.csv")
    plot_res_heatmeap()
    #plot_artificial_gap(2179)
    #plot_overlapping(2232)

