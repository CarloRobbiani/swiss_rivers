from txt_to_csv import missing, Read_txt
import pandas as pd


#air_df = Read_txt.read_air_temp("air_temp")
#air_df["tre200d0"] = pd.to_numeric(air_df["tre200d0"], errors="coerce")
#missing(air_df, "tre200d0")

#flow_df = Read_txt.read_hydro("hydro_data\Flow")
#flow_df["Wert"]= pd.to_numeric(flow_df["Wert"], errors="coerce")
#missing(flow_df, "Wert")

temp_df = Read_txt.read_hydro("hydro_data\Temp")
temp_df["Wert"]= pd.to_numeric(temp_df["Wert"], errors="coerce")
missing(temp_df, "Wert")

