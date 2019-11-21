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
    complPremium=0
    capitalCompl=8000

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()


#Retourne les primes pures   
    def purePremium(self):
        prem=self.p['POLPRVIEHT']-self.p['POLPRCPLA']
        return prem.to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
#Retourne les primes des garanties complémentaires    
    def premiumPrincipal(self):
        return self.purePremium()*self.nbrPolIfSM


#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):

#L'age limite est erroné, il faudra supprimer cette condition   
        agelimite=(self.age()<=65)
        
        riderIncPP=self.purePremium()*self.isPremPay()*agelimite
        riderIncPP2=self.purePremium()*agelimite
        precPP=self.zero()
        frek=self.frac().item(0,0,0)
        
        for i in range(1,self.shape[1]):
        
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek/12)*riderIncPP2[:,i,:])
            
        
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*self.nbrPolIf
        mathresIF=provMathIf
        
        
        
        annPremPP=self.p['POLPRVIEHT'].to_numpy()[:,np.newaxis,np.newaxis]
        CaFracPC=self.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        CaPremPC=self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        prInventPP=(annPremPP*(1-CaPremPC))/CaFracPC
        prPurePP=prInventPP
        ppEncPP=(prPurePP/self.frac())*self.isPremPay()
        pPureEnc=ppEncPP*self.nbrPolIfSM
        
           
        
        riderCostOutgo=self.premiumPrincipal()*self.dcAccident()*self.isPremPay()*agelimite
        
        mathResIfcorr=self.zero()       
        mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]
        reserve=mathResIfcorr+pPureEnc-riderCostOutgo
        reserve=np.maximum(reserve,0)
        
        return reserve


#Retourne les sinistres décès 
    def deathClaim(self):
        nbDeath=self.nbrDeath
        capitalDC=(self.p['POLPRCPLA']!=0)*self.capitalCompl
        capital=capitalDC.to_numpy()[:,np.newaxis,np.newaxis]
        return nbDeath*capital

#Retourne les sinistre complémentaire frais de visite    
    def accidentalDeathClaim(self):
        
        claimRate=self.dcAccident()

        
        premiumPrincipal=self.premiumPrincipal()
        
#Cette condition est erronée, car défini l'age terme à 65 ans pour la fin de garantie principale
        premiumPrincipal=(self.age()<=65)*premiumPrincipal
        
        claim=claimRate*premiumPrincipal*self.isPremPay()
        
        return claim

#Retourne le total des claim pour la garantie principale    
    def claimPrincipal(self):
        return self.accidentalDeathClaim()

#Retourne le total des claim pour les garanties complémentaires
    def claimCompl(self):
        return self.deathClaim()
    



##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def testerAX(self):
    return self

pol=AX()
#pol=AX(run=[4,5])

#pol.ids([2223701])
#pol.mod([70])
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
#u=pol.polTermM

#bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()



print("Class AX--- %s sec" %'%.2f'%  (time.time() - start_time))






##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self





monCas=riderCostOutgo

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)

#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])



#z=pol.p[pol.p['PMBPOL']==2509001]

#-->MathResIf a corriger

#L'age limite est erroné, il faudra supprimer cette condition   
        agelimite=(pol.age()<=65)
        
        riderIncPP=pol.purePremium()*pol.isPremPay()*agelimite
        riderIncPP2=pol.purePremium()*agelimite
        precPP=pol.zero()
        frek=pol.frac().item(0,0,0)
        
        for i in range(1,pol.shape[1]):
        
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek/12)*riderIncPP2[:,i,:])
            
        
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*pol.nbrPolIf
        mathresIF=provMathIf
        
        
        
        annPremPP=pol.p['POLPRVIEHT'].to_numpy()[:,np.newaxis,np.newaxis]
        CaFracPC=pol.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        CaPremPC=pol.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        prInventPP=(annPremPP*(1-CaPremPC))/CaFracPC
        prPurePP=prInventPP
        ppEncPP=(prPurePP/pol.frac())*pol.isPremPay()
        pPureEnc=ppEncPP*pol.nbrPolIfSM
        
           
        
        riderCostOutgo=pol.premiumPrincipal()*pol.dcAccident()*pol.isPremPay()*agelimite
        
        mathResIfcorr=pol.zero()       
        mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]
        reserve=mathResIfcorr+pPureEnc-riderCostOutgo
        reserve=np.maximum(reserve,0)



