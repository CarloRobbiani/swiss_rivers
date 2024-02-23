import matplotlib.pyplot as plt
from my_graph_reader import ResourceRiverReaderFactory
from matplotlib.widgets import Slider
import os
import pandas as pd
import datetime

def slider_to_date(value):
    date = start_date + datetime.timedelta(days=value)
    date =str(date) + " 00:00:00"
    return date

fig, ax = None, None


#Function to plot the river data
def plot_river_data(data, data_edges, date):

    global fig, ax
    ax.clear()
    # Plot the river nodes
    x = data[:,0]
    y = data[:,1]
    stations = data[:,2].tolist()
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
            df.set_index('Zeitstempel', inplace=True)
            values.append(int(pd.isna(df.loc[date, "Wert"])))
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

    # Calculate the total number of days between start and end dates
    start_date = datetime.date(1990, 1, 1)
    end_date = datetime.date(2021, 1, 1)
    total_days = (end_date - start_date).days

    # Create a matplotlib figure and axis
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    fig, ax = plt.subplots()
    ax_slider = plt.axes([0.1, 0.01, 0.65, 0.03])
    slider = Slider(ax_slider, 'Date', 0, total_days, valinit=0, valstep=1)
    init_date = slider_to_date(slider.val)
   

    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    def update(val):
        current_date = slider_to_date(slider.val)
        print(current_date)
        plot_river_data(data_x_rhein, data_edges_rhein, current_date)

    slider.on_changed(update)

    plot_river_data(data_x_rhein, data_edges_rhein, init_date)
    plt.show()

