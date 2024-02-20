import matplotlib.pyplot as plt
from my_graph_reader import ResourceRiverReaderFactory



#Function to plot the river data
def plot_river_data(data, data_edges):
    # Plot the river nodes
    x = data[:,0].numpy()
    y = data[:,1].numpy()
    plt.scatter(x, y, color='blue', label='River Nodes')

    # Plot the river edges
    for i in range(data_edges.shape[1]):
        start = data_edges[0, i]
        end = data_edges[1, i]
        plt.plot([x[start], x[end]], [y[start], y[end]], color='red')

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
