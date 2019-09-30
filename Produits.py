from Portefeuille import Portfolio
from Parametres import Hypo

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



#Calcul des inforce

    def inforce(self):
        
#        qxann = policies.qx(table=GKF95, exp=100,ass=1)
        qxmens = 1-(1-policies.qx(table=GKF95, exp=27.06,ass=1))**(1/12)
        
#        vectUN = policies.un
#        
#        nbmort = 
        
#        vectCor = np.multiply(vectUN[:-1], vectUN[1:], vectUN[1:])
        
#        inf = qxmens+ lapsemens
#        resultat = np.multiply(inf[:-1], inf[1:], inf[1:])
        
        return qxmens




sp=FU()       
b=sp.un
c=sp.vide
kk=policies.un

#d=sp.p
bbb = FU.inforce(policies)
z = FU.inforce(policies)

