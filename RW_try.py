from Parametres import allRuns, Hypo
from Portefeuille import Portfolio
from Produits import FU,AX,HO,PR,TE,VE,EP,MI
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
##############################################################################################################################

allSP=[Hypo,Portfolio,FU,AX,HO,PR,TE,VE,EP,MI]


instanceAllSP=pd.DataFrame()

allVar==pd.DataFrame()

for i in range(len(allSP)):
    
    sp=allSP[i]()
    
    instanceAllSP=instanceAllSP.append(sp)
    
    allVar=allVar(sp.__class__.__dict__.items())


allMethods=pd.DataFrame(set(allVar[0]))

a=set(allVar[0])

# d=MI()

# z=pd.DataFrame( d.__class__.__dict__.items())

# c=tuple(set(dir(d))-set(dir(a)))




print("Class RUN--- %s sec" %'%.2f'%  (time.time() - start_time))