import numpy as np
import torch
from normalizer import MinMaxNormalizer
from prediction import RecurrentPredictionModel
import json
import os

#order of normalizers: target, discharge, air, all the neighbours
class Model():

    def __init__(self, station, model_type, input_size):

        self.station = station
        self.model_type = model_type
        directory = f"models\{station}"
        

        files = [filename for filename in os.listdir(directory) if filename.endswith("normalizers.npy")]
        filename = files[-1]
        self.data = np.load(f"models/{station}/" + filename)

        self.read_npy_file()
        

        self.model = Model.read_metadata(station, model_type, input_size)
        #TODO check to automatize
        files = [filename for filename in os.listdir(directory) if filename.endswith(f"{model_type}.pt")]
        self.model.load_state_dict(torch.load(f"models/{station}/" + files[0]))
        self.model.eval()


    
    def a2gap(self, air_t):

        n_at = (self.normalizers[2].normalize(air_t))#.astype(float)
        n_at = np.float32(n_at)


        input_data = torch.tensor(n_at, dtype=torch.float32).unsqueeze(1)
        output = self.model(input_data) 
        #print(output)
        norm_output = self.normalizers[0].denormalize(output)

        return norm_output

    def aq2gap(self, air_t, discharge_t):
        
        n_at = (self.normalizers[2].normalize(air_t))
        n_at = np.float32(n_at)

        n_discharge = np.float32(self.normalizers[1].normalize(discharge_t))

        n_at = torch.tensor(n_at, dtype=torch.float32)
        n_discharge = torch.tensor(n_discharge, dtype=torch.float32)
        torch_input = torch.stack((n_discharge, n_at), dim=1)

        output = self.model(torch_input)
        norm_output = self.normalizers[0].denormalize(output)

        return norm_output

    #TODO Turn n_t list into a tensor?
    #TODO Stations with multiple neighbours? 
    def aqn2gap(self, air_t, q_target, n_t):

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


        #n_neighbours = torch.tensor(n_neighbours, dtype=torch.float32)
        torch_input = torch.stack(tensor_list, dim=1)

        output = self.model(torch_input)
        #print(output)
        norm_out = self.normalizers[0].denormalize(output)

        return norm_out

    def an2gap(self, air_t, n_t):

        n_at = (self.normalizers[2].normalize(air_t))
        n_at = np.float32(n_at)


        
        input_data = torch.tensor([[n_at]])#n_nei]])
        output = self.model(input_data) 
        #print(output)
        norm_out = self.normalizers[0].denormalize(output)
        return norm_out


    #station: ####; model: either at2wt/atq2wt/atqn2wt as a string
    #returns the model from the metadata
    def read_metadata(station, model, input_size):
        directory = f"models\{station}"
        prefix = f"{station}_{model}"

        filename = [filename for filename in os.listdir(directory) if filename.startswith(prefix)]
        
        f = open(f"C:/Users\carlo\OneDrive\Documents\GitHub\swiss_rivers\models/{station}/" + str(filename[0]))

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

    
            



if __name__ == "__main__":

    Model.read_metadata(2170, "at2wt")

    """ Models.atqn2gap()
    odel = np.load("models\Apr18_16-06-55_bnode052_11183649_3435_normalizers.npy")
    print(odel)
    odel2 = np.load("models\Apr18_17-07-55_bnode029_11185597_3423_normalizers.npy")
    print(odel2)
    tor = torch.load("models\Apr18_16-06-55_bnode052_11183649_3435_best_valid_loss_at2wt.pt")
    #print(tor) """