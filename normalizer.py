import numpy as np
class MinMaxNormalizer:
    ''' Normalizes a sequence such that the process is reversable
    '''

    def __init__(self, sequence):
        if sequence.min is not None:
            self.smin = sequence.min()
            self.smax = sequence.max()
        else:
            self.smin = np.min(sequence)
            self.smax = np.max(sequence)

    def normalize(self, sequence):
        return (sequence-self.smin)/(self.smax-self.smin)
    
    def denormalize(self, sequence):
        return (sequence*(self.smax-self.smin))+self.smin
