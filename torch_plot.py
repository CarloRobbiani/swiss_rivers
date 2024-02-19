import torch
import matplotlib.pyplot as plt
from my_graph_reader import ResourceRiverReaderFactory



#Function to plot the river data
def plot_river_data(data_x, data_edges):
    # Plot the river nodes
    plt.scatter(data_x[:, 0], data_x[:, 1], color='blue', label='River Nodes')

    # Plot the river edges
    for edge in data_edges:
        start = data_x[edge[0]]
        end = data_x[edge[1]]
        plt.plot([start[0], end[0]], [start[1], end[1]], color='black', linewidth=0.5)

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

    river_reader = ResourceRiverReaderFactory.rhein_reader()
    rhein_data_x, rhein_data_edges = river_reader.read()
    plot_river_data(rhein_data_x, rhein_data_edges)
