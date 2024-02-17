
import torch

class ResourceRiverReader():

    def __init__(self, river):
        self.river = river

    def read(self):
        data_x = torch.load(f'river_data/gewaesser_{self.river}_x.pt')
        data_edges = torch.load(f'river_data/gewaesser_{self.river}_edges.pt')
        return data_x, data_edges

class ResourceRiverReaderFactory():

    @staticmethod
    def aare_reader(suffix=''):
        return ResourceRiverReader(f'aare{suffix}')

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
        
