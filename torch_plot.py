import matplotlib.pyplot as plt
from my_graph_reader import ResourceRiverReaderFactory
import os
import pandas as pd



#Function to plot the river data
def plot_river_data(data, data_edges):
    # Plot the river nodes
    x = data[:,0]
    y = data[:,1]
    stations = data[:,2].numpy()
    files_flow = os.listdir("hydro_data\Flow")
    files_temp = os.listdir("hydro_data\Temp")
    values = []
    
    #temporary get first line and check for missing data
    for station in stations:
        file = [file for file in files_flow if file.startswith(str(station))]
        file.extend([file for file in files_temp if file.startswith(str(station))])

        
        if len(file) > 0:
            file_path = [f"hydro_data\Flow\{f}"if "Abfl" in f else "hydro_data\Temp\{f}" if "Wasser" in f else "" for f in file]
            df = pd.read_csv(file_path[0], delimiter=";", skiprows=8, encoding="iso-8859-1")
            values.append(pd.isna(df["Wert"].iloc[0]))
        else:
            values.append(1)


    colors = ["red" if value == 1 else "blue" for value in values]

    plt.scatter(x, y, color=colors, label='River Nodes')

    # Plot the river edges
    for i in range(data_edges.shape[1]):
        start = data_edges[0, i]
        end = data_edges[1, i]
        plt.plot([x[start], x[end]], [y[start], y[end]], color='black')

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('River Data')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    reader_inn = ResourceRiverReaderFactory.inn_reader()
    data_x_inn, data_edges_inn = reader_inn.read()
    plot_river_data(data_x_inn, data_edges_inn)

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()
    plot_river_data(data_x_rhein, data_edges_rhein)
