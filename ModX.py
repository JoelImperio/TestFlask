from iPortfolio import portfolio
from iHypothesis import hypo
import numpy as np
import pandas as pd


class modX(portfolio):
    mods=[8]
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        
z=portfolio().p
a=modX().p
e=modX().tout
b=modX().un
c=np.empty_like(b)
d=np.zeros_like(b)
