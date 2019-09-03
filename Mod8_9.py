from iPortfolio import Portfolio
from iHypothesis import Hypo
import numpy as np
import pandas as pd


class MOD8_9(Portfolio):
    mods=[8,9]
    
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        

sp=MOD8_9()       
b=sp.un
c=sp.vide
#d=sp.p




