from example_fill import fillers
import os
from neighbours import Neighbour
from txt_to_csv import Gaps


#Main procedure
#model_path: path the LSTM models are saved
#need_new_files: True if new files with NaN values are needed, False if they are already there
#file_list: The folder where the hydro data is saved e.g. "hydro_data"
#folder_save_path: where the new files with added NaN values should be saved to access them later
#prediction_save_path: where the prediction should be saved
def main_procedure(model_path, need_new_files, file_list, NaN_save_path, prediction_save_path):

    if need_new_files:
        Gaps.fill_gaps(file_list + "/Flow", NaN_save_path + "/Flow")
        Gaps.fill_gaps(file_list + "/Temp", NaN_save_path + "/Temp")

    big_adj = Neighbour.all_adj_list()

    for st in os.listdir(model_path):
        print(st)
        fillers.fill_a2gap(int(st), big_adj, NaN_save_path, prediction_save_path)
        fillers.fill_aq2gap(int(st), big_adj, NaN_save_path, prediction_save_path)
        fillers.fill_aqn2gap(int(st), big_adj, NaN_save_path, prediction_save_path)

        fillers.fill_aqn2gap_special(int(st), big_adj, NaN_save_path, prediction_save_path) 

        fillers.return_final_df(int(st), prediction_save_path, prediction_save_path, True) 


if __name__ == "__main__":
    main_procedure("models", False, "hydro_data", "filled_hydro", "predictions")
