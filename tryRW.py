from Portefeuille import Portfolio
from Parametres import Hypo

import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i

import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

#Importation d'une intance de Portfolio
p=Portfolio()



class myHypo(Hypo):

        def __init__(self):
            super().__init__()



class myFU(Portfolio):
    mods=[8,9]
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)





pol=myFU()
hyp=myHypo()














#start_time = time.time()
#
#
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))









