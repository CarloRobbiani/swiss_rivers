from my_graph_reader import ResourceRiverReader, ResourceRiverReaderFactory
from txt_to_csv import missing
import os
import pandas as pd
    
""" reader_inn = ResourceRiverReaderFactory.inn_reader()
data_x_inn, data_edges_inn = reader_inn.read()
print(data_x_inn)

reader_ti = ResourceRiverReaderFactory.ticino_reader()
data_x_inn, data_edges_inn = reader_ti.read()
print(data_x_inn)

reader_rhein = ResourceRiverReaderFactory.rhein_reader(-1990)
data_x_rhein, data_edges_rhein = reader_rhein.read()
print(data_edges_rhein)
print(data_x_rhein) 

for file in os.listdir("filled_hydro\Temp"):

    df = pd.read_csv("filled_hydro\Temp/" + file, delimiter=";")
    sorted = df.sort_values(by="Zeitstempel")

    missing(sorted, "Wert")

"""



