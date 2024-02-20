from my_graph_reader import ResourceRiverReader, ResourceRiverReaderFactory
    
reader_inn = ResourceRiverReaderFactory.inn_reader()
data_x_inn, data_edges_inn = reader_inn.read()
print(data_x_inn)

reader_ti = ResourceRiverReaderFactory.ticino_reader()
data_x_inn, data_edges_inn = reader_ti.read()
print(data_x_inn)

reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
data_x_rhein, data_edges_rhein = reader_rhein.read()
print(data_edges_rhein)
print(data_x_rhein)


