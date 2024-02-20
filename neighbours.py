from my_graph_reader import ResourceRiverReaderFactory
#Enter a data tensor and its edges and create a adjacency list.
def get_adj(data, edges):
    adj_list = {}
    for i in range(edges.shape[1]):
        start = data[edges[0,i], 2].item()
        end = data[edges[1,i], 2].item()
        if start not in adj_list:
            adj_list[start] = []
        adj_list[start].append(end)
        if end not in adj_list:
            adj_list[end] = []
        adj_list[end].append(start)
    return adj_list


#Enter station_nr and river from dataset in hydro data and return the neighbouring stations
#Problem: find right adj list
def get_neigbour(station, adj_list):
    if station not in adj_list:
        return []
    return adj_list[station]


if __name__== "__main__":
    reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
    data_x_rhein, data_edges_rhein = reader_rhein.read()

    adj_rhein = get_adj(data_x_rhein, data_edges_rhein)

    print("Neighbours: ", get_neigbour(2143, adj_rhein))
