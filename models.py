import numpy as np
import torch
from normalizer import MinMaxNormalizer
from prediction import RecurrentPredictionModel
import json

def a2gap(at1, at2):
    air_temp = np.array([13.2, 13.4])
    normalizer = MinMaxNormalizer(air_temp)
    n_at = normalizer.normalize(air_temp)
    #print(n_at)
    #print(normalizer.denormalize(n_at))

    f = open('C:/Users/carlo/OneDrive/Documents/GitHub/swiss_rivers\models/2372_at2wt_T1990_metadata.json')

    metadata = json.load(f)
    print(metadata["hyperparameters"])

    model = RecurrentPredictionModel(1, 
                                     int(metadata["hyperparameters"]["width"]),
                                     int(metadata["hyperparameters"]["depth"]),)
    
    model.load_state_dict(torch.load("models\Apr18_16-06-55_bnode052_11183649_3435_best_valid_loss_at2wt.pt"))
    input_data = torch.tensor([[0.5]])
    output = model.forward(input_data) 
    print(output)
    print(normalizer.denormalize(output))


def atqn2gap():
    air_temp = np.array([1.2, 13.4])
    discharge = np.array([4,7, 294])
    nei = np.array([3.8, 24])
    target = np.array([1.0, 14,4])
    norm_targ = MinMaxNormalizer(target)
    normalizer_air = MinMaxNormalizer(air_temp)
    normalizer_d = MinMaxNormalizer(discharge)
    normalizer_n = MinMaxNormalizer(nei)
    n_at = normalizer_air.normalize(air_temp)

    f = open("C:/Users\carlo\OneDrive\Documents\GitHub\swiss_rivers\models/2372_atqn2wt_T1990_N2104_metadata.json")
    metadata = json.load(f)
    model = RecurrentPredictionModel(3, 
                                     int(metadata["hyperparameters"]["width"]),
                                     int(metadata["hyperparameters"]["depth"]),)
    
    model.load_state_dict(torch.load("models\Apr18_17-07-55_bnode029_11185597_3423_best_valid_loss_atqn2wt.pt"))
    input_data = torch.tensor([[0.4,0.2,0.7]])
    output = model.forward(input_data) 
    print(output)
    print(norm_targ.denormalize(output))


if __name__ == "__main__":

    atqn2gap()
    odel = np.load("models\Apr18_16-06-55_bnode052_11183649_3435_normalizers.npy")
    print(odel)
    odel2 = np.load("models\Apr18_17-07-55_bnode029_11185597_3423_normalizers.npy")
    print(odel2)
    #tor = torch.load("models\Apr18_16-06-55_bnode052_11183649_3435_best_valid_loss_at2wt.pt")
    #print(tor)