import pandas as pd
import os

#get the percentages of usage for each model in the final prediction files
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