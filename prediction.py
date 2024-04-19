import torch.nn as nn
class RecurrentPredictionModel(nn.Module):

    ''' the classic air 2 water lstm '''

    def __init__(self, input_size, hidden_size, num_layers):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.linear = nn.Sequential(
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )
    
    def forward(self, x):
        out, hidden = self.lstm(x)
        target = self.linear(out)
        return target
