from Portefeuille import Portfolio
from Parametres import Hypo
import numpy as np
import pandas as pd

from MyPyliferisk import MortalityTable,vqx
from MyPyliferisk.mortalitytables import EKM95, EKF95


tariff = MortalityTable(nt=EKM95)




class FU(Portfolio):
    mods=[8,9]
    
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        

    def inforce(self):
        
        tariff2 = np.vectorize(qx)
        
        rqx = self.age1()
        
        return rqx

sp=FU()       
b=sp.un
c=sp.vide
#d=sp.p

z = FU.inforce(policies)

#print(tariff.qx[10])
