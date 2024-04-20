import os
import tensorflow
class FishNN():

    def __init__(self):
        self.fishNNDataFile = "fish_nn.tflearn"

        if os.path.exists(self.fishNNDataFile):
            self.nn_model.load(self.fishNNDataFile)