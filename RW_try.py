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


pggTotal=pd.DataFrame()
for i in range(len(allSP)):
    
    sp=allSP[i]()
    sp=pd.DataFrame(sp.__class__.__dict__.items())
    pggTotal=pggTotal.append(sp)

allMethods=pd.DataFrame(set(pggTotal[0]))

a=set(pggTotal[0])

# d=MI()

# z=pd.DataFrame( d.__class__.__dict__.items())

# c=tuple(set(dir(d))-set(dir(a)))




print("Class RUN--- %s sec" %'%.2f'%  (time.time() - start_time))