from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
#Création de la class X
##############################################################################################################################

    



##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def tester(self):
    return self

#pol=AX()
#pol=AX(run=[4,5])

#pol.ids([2222402,2511601,2547904,2556201,1764805,2372106,2540603])
#pol.mod([70])
#pol.modHead([70],2)

#a=pol.nbrPolIf
#b=pol.nbrPolIfSM
#c=pol.nbrMaturities
#d=pol.nbrDeath
#e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.purePremium()
#h=pol.deathClaim()
#i=pol.fraisVisiteClaim()
#j=pol.timeBeforeNextPay()
#k=pol.risqueEnCour()
#l=pol.adjustedReserve()
#m=pol.reserveExpense()
#n=pol.unitExpense()
#o=pol.totalPremium()
#q=pol.totalClaim()
#r=pol.totalCommissions()
#s=pol.totalExpense()
#t=pol.BEL()
#u=pol.polTermM

#bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()



print("Class X--- %s sec" %'%.2f'%  (time.time() - start_time))






##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self

monCas=a

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)

#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])



