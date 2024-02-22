import matplotlib.pyplot as plt
from my_graph_reader import ResourceRiverReaderFactory
from matplotlib.widgets import Slider
import os
import pandas as pd

fig, ax = None, None


#Function to plot the river data
def plot_river_data(data, data_edges):

    global fig, ax
    ax.clear()
    # Plot the river nodes
    x = data[:,0]
    y = data[:,1]
    stations = data[:,2]
    files_flow = os.listdir("hydro_data\Flow")
    files_temp = os.listdir("hydro_data\Temp")
    values = []
    
    #temporary get first line and check for missing data to get colors
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



    ax.scatter(x, y, color=colors, label='River Nodes')

    # Plot the river edges
    for i in range(data_edges.shape[1]):
        start = data_edges[0, i]
        end = data_edges[1, i]
        ax.plot([x[start], x[end]], [y[start], y[end]], color='black')

    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('River Data')
    ax.legend()
    ax.grid(True)

    fig.canvas.draw_idle()


if __name__ == "__main__":
    #reader_inn = ResourceRiverReaderFactory.inn_reader()
    #data_x_inn, data_edges_inn = reader_inn.read()
    #plot_river_data(data_x_inn, data_edges_inn)

    fig, ax = plt.subplots()
    ax_slider = plt.axes([0.1, 0.01, 0.65, 0.03])
    slider = Slider(ax_slider, 'Row Index', 0, 10, valinit=0, valstep=1)
   

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    def update():
        plot_river_data(data_x_rhein, data_edges_rhein)

    slider.on_changed(update)

    plot_river_data(data_x_rhein, data_edges_rhein)
    plt.show()

