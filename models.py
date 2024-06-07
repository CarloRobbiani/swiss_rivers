import numpy as np
import torch
from normalizer import MinMaxNormalizer
from prediction import RecurrentPredictionModel
import json
import os
from neighbours import Neighbour

#order of normalizers: target, discharge, air, all the neighbours
#order of input: discharge, air, neighbours
class Model():

    def __init__(self, station, model_type, input_size):

        self.station = station
        self.model_type = model_type
        directory = f"models/{station}"        

        self.model = Model.read_metadata(station, model_type, input_size)
        files = [filename for filename in os.listdir(directory) if filename.endswith(f"{model_type}.pt")] #TODO consider special cases
        
        npy_file = self.find_normalizer_for_model(files[-1], f"models/{station}")
        self.data = np.load(npy_file)
        self.read_npy_file() #load normalizers

        self.model.load_state_dict(torch.load(f"models/{station}/" + files[-1]))

        self.model.eval()


    
    def a2gap(self, air_t):
        air_t = air_t.astype("f")
        n_at = (self.normalizers[2].normalize(air_t))#.astype(float)
        n_at = np.float32(n_at)

        input_data = torch.tensor(n_at, dtype=torch.float32).unsqueeze(1)
        output = self.model(input_data) 
        norm_output = self.normalizers[0].denormalize(output)

        return norm_output

    def aq2gap(self, air_t, discharge_t):
        air_t = air_t.astype("f")
        
        n_at = (self.normalizers[2].normalize(air_t))
        n_at = np.float32(n_at)

        n_discharge = np.float32(self.normalizers[1].normalize(discharge_t))

        n_at = torch.tensor(n_at, dtype=torch.float32)
        n_discharge = torch.tensor(n_discharge, dtype=torch.float32)
        torch_input = torch.stack((n_discharge, n_at), dim=1)

        output = self.model(torch_input)
        norm_output = self.normalizers[0].denormalize(output)

        return norm_output


    def aqn2gap(self, air_t, q_target, n_t):
        air_t = air_t.astype("f")
        n_at = (self.normalizers[2].normalize(air_t))
        n_at = np.float32(n_at)
        n_discharge = np.float32(self.normalizers[1].normalize(q_target))
        tensor_list = []

        tensor_list.append(torch.tensor(n_discharge, dtype=torch.float32))
        tensor_list.append(torch.tensor(n_at, dtype=torch.float32))

        for i in range(len(n_t)):
            norm_index = i+3
            value_n = np.float32(self.normalizers[norm_index].normalize(n_t[i]))
            tensor_list.append(torch.tensor(value_n, dtype=torch.float32))

        #immer reihenfolge beibahlten wei bei files

        torch_input = torch.stack(tensor_list, dim=1)

        output = self.model(torch_input)
        norm_out = self.normalizers[0].denormalize(output)

        return norm_out

    def an2gap(self, air_t, n_t):
        air_t = air_t.astype("f")        
        tensor_list = []

        n_at = (self.normalizers[2].normalize(air_t))
        n_at = np.float32(n_at)
        tensor_list.append(torch.tensor(n_at, dtype=torch.float32))

        for i in range(len(n_t)):
            norm_index = i+3
            value_n = np.float32(self.normalizers[norm_index].normalize(n_t[i]))
            tensor_list.append(torch.tensor(value_n, dtype=torch.float32))
        
        torch_input = torch.stack(tensor_list, dim=1)

        output = self.model(torch_input)
        norm_out = self.normalizers[0].denormalize(output)


    #station: ####; model: either at2wt/atq2wt/atqn2wt as a string
    #returns the model from the metadata
    def read_metadata(station, model, input_size):
        directory = f"models/{station}"

        prefix = f"{station}_{model}"


        filename = [filename for filename in os.listdir(directory) if filename.startswith(prefix)]
        
        #f = open(f"C:/Users/carlo/OneDrive/Documents/GitHub/swiss_rivers/models/{station}/" + str(filename[0]))
        f = open(f"models/{station}/" + str(filename[-1]))

        metadata = json.load(f)
        model = RecurrentPredictionModel(input_size, 
                                        int(metadata["hyperparameters"]["width"]),
                                        int(metadata["hyperparameters"]["depth"]),)
        
        return model

    #returns an array of normalizers in the stated order
    def read_npy_file(self):
        self.arr = []
        self.normalizers = []
        for row in self.data:
            self.arr.append([row[1], row[2]])

        for item in self.arr:
            self.normalizers.append(MinMaxNormalizer(np.array(item, dtype=np.float32)))

    #selects the normalizer file corrsponding to the model .pt file
    def find_normalizer_for_model(self, model_file, directory):
        
        files = os.listdir(directory)
        files = sorted(files)
        
        # Find the index of the given model file in the sorted list
        model_filename = os.path.basename(model_file)
        model_index = files.index(model_filename)
        
        # Check if the next file is a normalizer file
        if model_index < len(files) - 1 and files[model_index + 1].endswith(".npy"):
            normalizer_file = os.path.join(directory, files[model_index + 1])
            return normalizer_file
        else:
            return None

    
if __name__ == "__main__":

    #Model.read_metadata(2170, "at2wt")

    """ Models.atqn2gap()
    odel = np.load("models/Apr18_16-06-55_bnode052_11183649_3435_normalizers.npy")
    print(odel)
    odel2 = np.load("models/Apr18_17-07-55_bnode029_11185597_3423_normalizers.npy")
    print(odel2)
    tor = torch.load("models/Apr18_16-06-55_bnode052_11183649_3435_best_valid_loss_at2wt.pt")
    #print(tor) """