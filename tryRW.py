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
#Création de la class Axiprotect
##############################################################################################################################
class AX(Portfolio):
    mods=[70]


    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()








##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def testerAX(self):
    return self

pol=AX()
#pol=AX(run=[4,5])

#pol.ids([2475501,2236203])
#pol.mod([9])
#pol.modHead([9],2)

a=pol.nbrPolIf
b=pol.nbrPolIfSM
c=pol.nbrMaturities
d=pol.nbrDeath
e=pol.nbrSurrender
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

#bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()





print("Class AX--- %s sec" %'%.2f'%  (time.time() - start_time))






##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self





monCas=a

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z.to_csv(r'check.csv')

#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])



#z=pol.p[pol.p['PMBPOL']==2509001]


