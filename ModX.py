from iPortfolio import portfolio
from iHypothesis import hypo
import numpy as np
import pandas as pd


class modX(portfolio):
    mods=[8]
    
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        

sp=modX()       
a=sp.vide
b=sp.ids([6401])
c=sp.vide
d=sp.p




