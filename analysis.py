from txt_to_csv import Gaps, Read_txt
import pandas as pd
import os


#air_df = Read_txt.read_air_temp("air_temp")
#air_df["tre200d0"] = pd.to_numeric(air_df["tre200d0"], errors="coerce")
#missing(air_df, "tre200d0")

#flow_df = Read_txt.read_hydro("hydro_data\Flow")
#flow_df["Wert"]= pd.to_numeric(flow_df["Wert"], errors="coerce")
#missing(flow_df, "Wert")

#temp_df = Read_txt.read_hydro("hydro_data\Temp")
#miss_date(temp_df)
#temp_df["Wert"]= pd.to_numeric(temp_df["Wert"], errors="coerce")
#missing(temp_df, "Wert")

def get_percentages():


    model_names = ["A2Gap", "AQ2Gap", "AQN2Gap"]
    models = []

    stations = os.listdir("predictions")
    for st in stations:
        df = pd.read_csv(f"predictions\{st}/Temp_final_{st}.csv", delimiter=",")
        df = df[df["Model"] != "Source"]
        models.extend(df["Model"].tolist())

    total_len = len(models)

    for m in model_names:
        m_list = [mod for mod in models if m == mod]
        len_m = len(m_list)
        p = len_m / total_len * 100
        print(f"Model {m} precentage: {p}")






if __name__ == "__main__":
    get_percentages()