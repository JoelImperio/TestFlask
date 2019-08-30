from iPortfolio import Portfolio
from iHypothesis import Hypo
import numpy as np
import pandas as pd


class MODX(Portfolio):
    mods=[8]
    
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        

sp=MODX()       
a=sp.lapse
b=sp.un
c=sp.vide
#d=sp.p




