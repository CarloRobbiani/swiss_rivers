from txt_to_csv import find_missing_dates, Read_txt, miss_date
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


#Method that takes the hydro data and adds NaN for the column "Wert" entries where there are no dates
#File_list: Folder with the original temp/flow data
#folder_save_path: the folder where the data should be saved to
def fill_gaps(file_list, folder_save_path):
    for file in os.listdir(file_list):
        file_path = file_list + "/" + file
        df = pd.read_csv(file_path, delimiter=';', skiprows=8, encoding="iso-8859-1")
        missings = find_missing_dates(df)

        for date in missings:
            new_row = {'Stationsname': df['Stationsname'].iloc[0],
        'Stationsnummer': df['Stationsnummer'].iloc[0],
        'Parameter': df['Parameter'].iloc[0],
        'Zeitreihe': df['Zeitreihe'].iloc[0],
        'Parametereinheit': df['Parametereinheit'].iloc[0],
        'Gewässer': df['Gewässer'].iloc[0],
        'Zeitstempel': str(date),
        'Zeitpunkt_des_Auftretens': None,
        'Wert': None,
        'Freigabestatus': "hinzugefügte Daten"}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        path = folder_save_path + "/" + str(file)
        df.to_csv(path, sep=";", index = False)

if __name__ == "__main__":
    fill_gaps("hydro_data/Flow", "filled_hydro/Flow")