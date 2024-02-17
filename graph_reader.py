
import torch

# TODO: remove Aare Reader

class AareReader:

    def read(self):
        data_x = torch.load('swissrivernetwork/reader/gewaesser_aare_x.pt') # yes we know, Aare includes Rhein
        data_edges = torch.load('swissrivernetwork/reader/gewaesser_aare_edges.pt')
        return data_x, data_edges
    
    def my_read(self):
        data_x = torch.load('C:\Bachelorarbeit\Graphes/river_data\gewaesser_inn_x.pt') # yes we know, Aare includes Rhein
        data_edges = torch.load('C:\Bachelorarbeit\Graphes/river_data/gewaesser_inn_edges.pt')
        return data_x, data_edges

class ResourceRiverReader():

    def __init__(self, river):
        self.river = river

    def read(self):
        data_x = torch.load(f'swissrivernetwork/resources/rivers/gewaesser_{self.river}_x.pt')
        data_edges = torch.load(f'swissrivernetwork/resources/rivers/gewaesser_{self.river}_edges.pt')
        return data_x, data_edges

class ResourceRiverReaderFactory():

    @staticmethod
    def rhein_reader(suffix=''):
        return ResourceRiverReader(f'rhein{suffix}')
    
    @staticmethod
    def rohne_reader(suffix=''):
        return ResourceRiverReader(f'rhone{suffix}')
    
    @staticmethod
    def inn_reader(suffix=''):
        return ResourceRiverReader(f'inn{suffix}')
    
    @staticmethod
    def ticino_reader(suffix=''):
        return ResourceRiverReader(f'ticino{suffix}')
        
