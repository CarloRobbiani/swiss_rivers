import numpy as np
import torch
from normalizer import MinMaxNormalizer
from prediction import RecurrentPredictionModel
import json
import os

class Models:
    #TODO anstatt nur ein value für air_t gib als input langer vektor
    def a2gap(air_t, station):

        data = np.load("models/2481\Apr19_20-24-04_bnode051_11243919_1797_normalizers.npy")
        t_low, t_high = map(float, data[0][1:])
        air_low, air_high = map(float, data[2][1:])
        wt_n_low, wt_n_high = map(float, data[3][1:])

        air_temp = np.array([air_low, air_high])
        target = np.array([t_low, t_high])
        norm_t = MinMaxNormalizer(target)
        normalizer_air = MinMaxNormalizer(air_temp)
        #air_t = air_t.numpy()
        n_at = (normalizer_air.normalize(air_t))#.astype(float)
        n_at = np.float32(n_at)

        #print(metadata["hyperparameters"])

        model = Models.read_metadata(station, "at2wt", 1)

        model.load_state_dict(torch.load("models/2481\Apr19_19-21-53_bnode041_11243843_1794_best_valid_loss_at2wt.pt"))

        model.eval()

        #input_data = torch.tensor([n_at])
        input_data = torch.tensor(n_at, dtype=torch.float32).unsqueeze(1)
        output = model(input_data) 
        #print(output)
        norm_output = norm_t.denormalize(output)

        return norm_output

    #TODO Turn n_t list into a tensor?
    #TODO Stations with multiple neighbours? Maybe dont denormalize them in fill function?
    def atqn2gap(air_low, air_high, air_t, q_low, q_high, q_target, t_low, t_high, n_low, n_high, n_t, station):
        air_temp = np.array([air_low, air_high])
        discharge = np.array([q_low, q_high])
        nei = np.array([n_low, n_high])
        target = np.array([t_low, t_high])
        norm_targ = MinMaxNormalizer(target)
        normalizer_air = MinMaxNormalizer(air_temp)
        normalizer_d = MinMaxNormalizer(discharge)
        normalizer_n = MinMaxNormalizer(nei)
        n_at = float(normalizer_air.normalize(air_t))
        n_q = float(normalizer_d.normalize(q_target))
        #n_nei = float(normalizer_n.normalize(n_t[0].item()))
        n_nei = float(normalizer_n.normalize(n_t))

        model = Models.read_metadata(station, "atqn2wt", 3)
        
        model.load_state_dict(torch.load("models/2481\Apr19_20-24-04_bnode051_11243919_1797_best_valid_loss_atqn2wt.pt"))
        #immer reihenfolge beibahlten wei bei files
        input_data = torch.tensor([[n_at,n_q,n_nei]])
        output = model.forward(input_data) 
        #print(output)
        norm_out = norm_targ.denormalize(output)

        return norm_out

    def atn2gap(air_low, air_high, air_t, t_low, t_high, n_low, n_high, n_t, station):
        air_temp = np.array([air_low, air_high])
        nei = np.array([n_low, n_high])
        target = np.array([t_low, t_high])
        norm_targ = MinMaxNormalizer(target)
        normalizer_air = MinMaxNormalizer(air_temp)
        normalizer_n = MinMaxNormalizer(nei)
        n_at = normalizer_air.normalize(air_t)
        n_nei = normalizer_n.normalize(n_t[0].item())

        model = Models.read_metadata(station, "atn2wt", 2)
        
        model.load_state_dict(torch.load("models/2481\Apr19_19-49-54_bnode058_11243851_1797_best_valid_loss_atq2wt.pt"))
        input_data = torch.tensor([[n_at,n_nei]])
        output = model.forward(input_data) 
        #print(output)
        norm_out = norm_targ.denormalize(output)
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


if __name__ == "__main__":

    Models.read_metadata(2170, "at2wt")

    """ Models.atqn2gap()
    odel = np.load("models\Apr18_16-06-55_bnode052_11183649_3435_normalizers.npy")
    print(odel)
    odel2 = np.load("models\Apr18_17-07-55_bnode029_11185597_3423_normalizers.npy")
    print(odel2)
    tor = torch.load("models\Apr18_16-06-55_bnode052_11183649_3435_best_valid_loss_at2wt.pt")
    #print(tor) """