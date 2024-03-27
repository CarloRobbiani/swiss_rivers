from my_graph_reader import ResourceRiverReader, ResourceRiverReaderFactory
from txt_to_csv import Gaps
import os
import pandas as pd
""" 
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

for file in os.listdir("filled_hydro\Temp"):

    df = pd.read_csv("filled_hydro\Temp/" + file, delimiter=";", encoding="latin1")
    sorted = df.sort_values(by="Zeitstempel")

    Gaps.missing_len(sorted, "Wert", True)



#df = pd.read_csv("filled_hydro/Temp/2109_Wassertemperatur.txt",  delimiter=";", encoding="latin1")
#print(df.head())
#print(df["Gewässer"].iloc[0])

print(Gaps.missing_len(df, "Wert", True))
"""
#print(Gaps.find_gap_length(2143, "2001-01-01 00:00:00"))
#print(Gaps.gaps_with_dates(2499))

df = pd.read_parquet(f"parquet_hydro\Temp/2091_Wassertemperatur.parquet")
df = df.sort_values(by="Zeitstempel")

#df = pd.read_csv("filled_hydro/Temp/2091_Wassertemperatur.txt",  delimiter=";", encoding="latin1")

df = Gaps.gaps_with_dates(2091)
print(df.head())




