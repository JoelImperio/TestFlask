from Portefeuille import Portfolio
from Parametres import Hypo
<<<<<<< HEAD
import numpy as np
import pandas as pd

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM95, EKF95


tariff = MortalityTable(nt=EKM95)



import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i

import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

#Ceci est une class d'exemple pour reprendre merci de ne pas toucher
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
<<<<<<< HEAD
#d=sp.p
bbb = FU.inforce(policies)
z = FU.inforce(policies)

