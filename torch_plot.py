import matplotlib.pyplot as plt
from graph_reader import ResourceRiverReaderFactory
from matplotlib.widgets import Slider
import os
import pandas as pd
import datetime
import torch


#plots both the old stations and the new stations
def plot_river_data_both(data_2010, data_edges_2010, data_1990, data_edges_1990):
    #fig, ax = plt.subplots(2)

    x_2010 = data_2010[:,0]
    y_2010 = data_2010[:,1]
    x_1990 = data_1990[:,0]
    y_1990 = data_1990[:,1]
    #stations_2010 = data_2010[:,2].tolist()




    plt.scatter(x_2010, y_2010, label='River Nodes 2010', c = "Red")
    plt.scatter(x_1990, y_1990, label='River Nodes 1990')

    for i, row in enumerate(data_2010.numpy()):
        x = row[0]
        y = row[1]
        text = row[2]

        plt.annotate(str(text), xy=(x,y), xytext=(x+200, y+200))


 

    # Plot the river edges
    for i in range(data_edges_2010.shape[1]):
        start = data_edges_2010[0, i]
        end = data_edges_2010[1, i]
        plt.plot([x_2010[start], x_2010[end]], [y_2010[start], y_2010[end]], color='black')

    """ for i in range(data_edges_1990.shape[1]):
        start = data_edges_1990[0, i]
        end = data_edges_1990[1, i]
        plt.plot([x_1990[start], x_1990[end]], [y_1990[start], y_1990[end]], color='black') """

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('River Data Rhein')
    plt.legend()

    plt.show()


def create_special_graph_missing_neighbours(data_rhein, data_rhone):
    stations_rhein = [2288, 2473, 2143, 2282, 2085, 2386, 2044]
    stations_rhone = [2606, 2174, 2009]

    mask_rhein = torch.tensor([elem[-1] in stations_rhein for elem in data_rhein])

    tensor_x_rhein = data_rhein[mask_rhein]
    tensor_edges_rhein = torch.tensor([[2, 2, 6, 3],
                                       [0, 4, 5, 1]])
    print(tensor_edges_rhein)
    torch.save(tensor_x_rhein, "river_data\gewaesser_special_rhein_missing_n_x.pt")
    torch.save(tensor_edges_rhein, "river_data\gewaesser_special_rhein_missing_n_edges.pt")

    mask_rhone = torch.tensor([elem[-1] in stations_rhone for elem in data_rhone])

    tensor_x_rhone = data_rhone[mask_rhone]
    tensor_edges_rhone = torch.tensor([[1, 1],
                                       [0, 2,]])
    print(tensor_edges_rhone)
    torch.save(tensor_x_rhone, "river_data\gewaesser_special_rhone_missing_n_x.pt")
    torch.save(tensor_edges_rhone, "river_data\gewaesser_special_rhone_missing_n_edges.pt")


def create_special_graph_rhein(data_2010):
    stations = [2179, 2308, 2033,2126 ,2410 ,2150 ,2327, 2085, 2143, 2044, 2109, 2019, 2030, 2473]

    mask = torch.tensor([elem[-1] in stations for elem in data_2010])

    tensor_x = data_2010[mask]
    tensor_edges = torch.tensor([[10, 2, 5, 9, 3, 4, 6, 12, 13, 7],
                                       [8, 0, 0, 1, 0, 0, 0, 11, 11, 0]])

    print(tensor_edges)
    torch.save(tensor_x, "river_data\gewaesser_special_rhein_x.pt")
    torch.save(tensor_edges, "river_data\gewaesser_special_rhein_edges.pt")

def create_special_graph_rhone(data_2010):
    stations = [2432, 2009, 2174]

    mask = torch.tensor([elem[-1] in stations for elem in data_2010])

    tensor_x = data_2010[mask]
    tensor_edges = torch.tensor([[2, 1],
                                [0, 0]])

    torch.save(tensor_x, "river_data\gewaesser_special_rhone_x.pt")
    torch.save(tensor_edges, "river_data\gewaesser_special_rhone_edges.pt")

def create_special_graph_inn(data_2010):
    stations = [2617, 2462]

    mask = torch.tensor([elem[-1] in stations for elem in data_2010])

    tensor_x = data_2010[mask]
    tensor_edges = torch.tensor([[0],
                                [1]])

    print(tensor_edges)
    torch.save(tensor_x, "river_data\gewaesser_special_inn_x.pt")
    torch.save(tensor_edges, "river_data\gewaesser_special_inn_edges.pt")

def create_special_graph_ti(data_2010):
    stations = [2167, 2068, 2612]

    mask = torch.tensor([elem[-1] in stations for elem in data_2010])

    tensor_x = data_2010[mask]
    tensor_edges = torch.tensor([[0, 2],
                                [1, 1]])

    torch.save(tensor_x, "river_data\gewaesser_special_ti_x.pt")
    torch.save(tensor_edges, "river_data\gewaesser_special_ti_edges.pt")

def plot_special(data_x, data_edges):

    x_data = data_x[:,0]
    y_data = data_x[:,1]


    plt.scatter(x_data, y_data, label='River Nodes special cases', c = "Blue")


    for i, row in enumerate(data_x.numpy()):
        x = row[0]
        y = row[1]
        text = row[2]

        plt.annotate(str(text), xy=(x,y), xytext=(x+200, y+200))



    # Plot the river edges
    for i in range(data_edges.shape[1]):
        start = data_edges[0, i]
        end = data_edges[1, i]
        plt.plot([x_data[start], x_data[end]], [y_data[start], y_data[end]], color='black')

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('River Data Rhein')
    plt.legend()

    plt.show()



if __name__ == "__main__":
    # Calculate the total number of days between start and end dates
    start_date = datetime.date(1990, 1, 1)
    end_date = datetime.date(2021, 1, 1)
    total_days = (end_date - start_date).days

  
    

    reader_rhein_1990 = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein_1990, data_edges_rhein_1990 = reader_rhein_1990.read()

    reader_rhein_2010 = ResourceRiverReaderFactory.rhein_reader(-2010)
    data_x_rhein_2010, data_edges_rhein_2010 = reader_rhein_2010.read()

    reader = ResourceRiverReaderFactory.ticino_special_reader()
    data_x, data_edges = reader.read()
    #plot_special(data_x, data_edges)
    

    
    reader_rhone_1990 = ResourceRiverReaderFactory.rohne_reader(-1990)
    data_x_rhone_1990, data_edges_rhone_1990 = reader_rhone_1990.read()

    reader_rhone_2010 = ResourceRiverReaderFactory.rohne_reader(-2010)
    data_x_rhone_2010, data_edges_rhone_2010 = reader_rhone_2010.read() 
    
    
    reader_ti = ResourceRiverReaderFactory.ticino_reader()
    data_x_ti, data_edges_ti = reader_ti.read()

    reader = ResourceRiverReaderFactory.rhein_missing_n_reader()
    data_x, data_edges = reader.read()
    plot_special(data_x, data_edges)

    #plot_special(data_x_ti, data_edges_ti)
    """

    reader_inn = ResourceRiverReaderFactory.inn_reader()
    data_x, data_edges = reader_inn.read() """
    

    #plot_river_data_both(data_x_rhein_2010, data_edges_rhein_2010, data_x_rhein_1990, data_edges_rhein_1990)
    #plot_river_data_both(data_x_rhone_2010, data_edges_rhone_2010, data_x_rhone_1990, data_edges_rhone_1990)


