from txt_to_csv import read_air_temp
import pandas as pd


test_df = read_air_temp("air_temp")

missing_air = test_df[test_df.iloc[:,-1] == "-"]

print(missing_air) #1382 missing values

