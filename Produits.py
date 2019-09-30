from Portefeuille import Portfolio
from Parametres import Hypo
import numpy as np
import pandas as pd

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM95, EKF95


tariff = MortalityTable(nt=EKM95)




class FU(Portfolio):
    mods=[8,9]
    
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        


#Il faut vectorisé ici la fonction des qx

    def inforce(self):
        
        self.un = self.one()
        qx1 = tariff.qx[self.age1()] * self.un
        qx2 = tariff.qx[self.age2()] * self.un
        
        return qx1, qx2



sp=FU()       
b=sp.un
c=sp.vide
#d=sp.p
bbb = FU.inforce(policies)
z = FU.inforce(policies)

#print(tariff.qx[10])
