import numpy as np
import torch
from normalizer import MinMaxNormalizer
from prediction import RecurrentPredictionModel
import json


if __name__ == "__main__":

    air_temp = np.array([13.2, 13.4])
    normalizer = MinMaxNormalizer(air_temp)
    n_at = normalizer.normalize(air_temp)
    #print(n_at)
    #print(normalizer.denormalize(n_at))

    f = open('C:/Users/carlo/OneDrive/Documents/GitHub/swiss_rivers\models/2372_at2wt_T1990_metadata.json')

    metadata = json.load(f)
    print(metadata["hyperparameters"])

    model = RecurrentPredictionModel(2, 
                                     int(metadata["hyperparameters"]["width"]),
                                     int(metadata["hyperparameters"]["depth"]),)
    print(model.forward(n_at))    
    #model = np.load("models\Apr18_16-06-55_bnode052_11183649_3435_normalizers.npy")
    #print(model)
    #tor = torch.load("models\Apr18_16-06-55_bnode052_11183649_3435_best_valid_loss_at2wt.pt")
    #print(tor)