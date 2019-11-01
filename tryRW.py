from Portefeuille import Portfolio
from Parametres import allRuns
from Produits import FU
import numpy as np
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
##############################################################################################################################
class RUNPGG():

    def __init__(self):
        self

    def pggParSousPortefeuille(self,runNumber=allRuns):
        
        
        fu=FU(run=runNumber).PGG()
        mi=FU(run=runNumber).PGG()
        
        pggTotal=pd.DataFrame(fu)
        pggTotal=pggTotal.append(mi)
        
        
        return pggTotal
    
    def pggTotal(self):
        
        spPGG=self.pggParSousPortefeuille()
        
        spPGG=sum(spPGG['PGG'])
        
        return spPGG
        
        
 
run=RUNPGG()

a=run.pggParSousPortefeuille()
b=run.pggTotal()

b=a.copy()
a['Etape']='Sinistralité'
b['Etape']='Lapse'

c=a.append(b)

d=c.groupby(['Etape']).sum()


print("Class RUN--- %s sec" %'%.2f'%  (time.time() - start_time))
##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self





#monCas=y
#
#zz=np.sum(monCas, axis=0)
#zzz=np.sum(zz[:,0])
#z=pd.DataFrame(monCas[:,:,0])
#z.to_csv(r'check.csv')

#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])






