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
#Création de la class Preciso et Preciso Plus
############################################################################################################################

class EP(Portfolio):
    mods=[28,29,30,31,32,33,36]


    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopSaving()


#Retourne les primes pures   
    def purePremium(self):
        prem=self.p['POLPRVIEHT']
        return prem.to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    


#Retourne le total des claim pour la garantie principale    
    def claimPrincipal(self):
        return self.deathClaim()

#Retourne le total des claim pour les garanties complémentaires
    def claimCompl(self):
        return self.accidentalDeathClaim() 

#Retourne les primes totales perçues
    def totalPremium(self):
        premInc=(self.p['POLPRTOT'])[:,np.newaxis,np.newaxis]/self.frac()
        
        
        prem=premInc*self.nbrPolIfSM*self.isPremPay()*self.indexation()
        
        return prem

# Créer un vecteur de temporel en année depuis le début de la projection qui dépend du duration if
    def indexation(self):
        
        durif = self.p['DurationIfInitial'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()-1
        durif = np.remainder(durif, 12)
        increment = np.cumsum(self.one(), axis = 1) -1 + durif
        increment = increment/12
        increment = np.floor(increment)
        
        indexation=(self.one()+(self.p['POLINDEX'].to_numpy()[:,np.newaxis,np.newaxis]/100) )**increment
        
        return indexation

##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################









def tester(self):
    return self

pol = EP()
#pol=EP(run=[4,5])
# pol.ids([363001])
# pol.ids([1900401])
# pol.ids([1777802])
pol.ids([515503,1736301,1900401,2168101,2396001,2500001,2500101,2466301])

# pol.mod([36])
#pol.modHead([9],2)
aa = pol.p
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
# l=pol.adjustedReserve()
#m=pol.reserveExpense()
#n=pol.unitExpense()
o=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()

# bel=np.sum(pol.BEL(), axis=0)
# pgg=pol.PGG()

a=pol.indexation()

monCas=o

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)


# aaa=aa[['PMBPOL', 'PMBFRACT','POLSIT','PMBMOD','PMBTXINT']]


# aa.to_excel("check portefeuille.xlsx", header = True )


#Visualiser une dimension d'un numpy qui n'apparait pas
#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])



