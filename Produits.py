from Portefeuille import Portfolio
from Parametres import allRuns
import numpy as np
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
##############################################################################################################################


##############################################################################################################################
#Création de la class Funérailles
##############################################################################################################################
class FU(Portfolio):
    mods=[8,9]
    complPremium=60

    
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
###########################################DEBUT DES VARIABLES PRODUITS#######################################################
##############################################################################################################################
 
#Retourne les primes des garanties complémentaires    
    def premiumCompl(self):
        return (self.complPremium/self.frac())*self.nbrPolIfSM

#Retourne les primes pures de la garantie principale 
    def purePremium(self):
        return self.p['POLPRDECES'].to_numpy()[:,np.newaxis,np.newaxis]/self.frac()

#Retourne les risque en cours, soit les primes émises non aquises
    def risqueEnCour(self):
        
        elapseTime=self.timeBeforeNextPay()
        
        purePremium=self.purePremium()
        
        reserve=purePremium*elapseTime*self.nbrPolIf 
                      
        return reserve
  
#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):
        
        prPurePP=((self.p['POLPRTOT']- self.complPremium)*(1-self.p['aquisitionLoading'])).to_numpy()[:,np.newaxis,np.newaxis]
        pPureEncPP= (prPurePP/self.frac())*self.nbrPolIfSM*self.isPremPay()

        riderCost=self.claimCompl()
        
        risqueEnCour=self.risqueEnCour()
        risqueEnCour=np.roll(risqueEnCour,[1],axis=1)
        risqueEnCour[:,0,:]=0       
        
        reserve=np.maximum(pPureEncPP-riderCost+risqueEnCour,0)
        
        return reserve

#Retourne les sinistres décès 
    def deathClaim(self):
        nbDeath=self.nbrDeath
        capital=self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]
        return nbDeath*capital
    
#Retourne les sinistre complémentaire frais de visite    
    def fraisVisiteClaim(self):
        
        claimRate=self.fraisVisite()
        
        premiumCompl=self.premiumCompl()
        
        claim=claimRate*premiumCompl*self.isPremPay()
        
        return claim

#Retourne le total des claim pour la garantie principale    
    def claimPrincipal(self):
        return self.deathClaim()

#Retourne le total des claim pour les garanties complémentaires
    def claimCompl(self):
        return self.fraisVisiteClaim()
    


  

##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def tester(self):
    return self

pol=FU()
pol=AX()
#pol=FU(run=[4,5])

#pol.ids([2142501])
#pol.mod([9])
#pol.modHead([9],2)

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

#bel=np.sum(pol.BEL(), axis=0)
pgg=pol.PGG()



print("Class FU--- %s sec" %'%.2f'%  (time.time() - start_time))







