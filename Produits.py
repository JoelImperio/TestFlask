from Portefeuille import Portfolio
from Parametres import Hypo
import numpy as np
import pandas as pd


class FU(Portfolio):
    mods=[8,9]
    
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        

sp=FU()       
b=sp.un
c=sp.vide
#d=sp.p




