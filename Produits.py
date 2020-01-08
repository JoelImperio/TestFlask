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
    
print("Class FU--- %s sec" %'%.2f'%  (time.time() - start_time))

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

#L'age limite est erroné, il faudra supprimer cette condition  
        self.agelimite=(self.age()<=65)

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

        
        #Calcul du risque en cours
        riderIncPP=self.purePremium()*self.isPremPay()*self.agelimite
        riderIncPP2=self.purePremium()*self.agelimite
        precPP=self.zero()
        frek=self.frac()
 

        for i in range(1,self.shape[1]):
        
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
                   
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*self.nbrPolIf
        mathresIF=provMathIf
        
        mathResIfcorr=self.zero()       
        mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]        
        
        #Primes pure encaissées
        annPremPP=self.p['POLPRVIEHT'].to_numpy()[:,np.newaxis,np.newaxis]
        CaFracPC=self.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        CaPremPC=self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        prInventPP=(annPremPP*(1-CaPremPC))/CaFracPC
        prPurePP=prInventPP
        ppEncPP=(prPurePP/self.frac())*self.isPremPay()
        pPureEnc=ppEncPP*self.nbrPolIfSM
        
           
        #Sortie pour les claim principaux
        riderCostOutgo=self.premiumPrincipal()*self.dcAccident()*self.isPremPay()*self.agelimite
        

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
        

        premiumPrincipal=premiumPrincipal*self.agelimite
        
        claim=claimRate*premiumPrincipal*self.isPremPay()
        
        return claim

#Retourne le total des claim pour la garantie principale    
    def claimPrincipal(self):
        return self.accidentalDeathClaim()

#Retourne le total des claim pour les garanties complémentaires
    def claimCompl(self):
        return self.deathClaim() 

print("Class AX--- %s sec" %'%.2f'%  (time.time() - start_time))





##############################################################################################################################
#Création de la class Hospitalis
##############################################################################################################################

class HO(Portfolio):
    mods=[58]
    ageLimite = 75

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()


#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):

        # Age limite pour hospitalis
        self.agelimite=((self.age()-1)<=self.ageLimite)
           
        annualPrem = (self.p['POLPRVIEHT'] + self.p['POLPRCPL2']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()   
 
        self.agelimite = self.agelimite * self.one()
        
        #Calcul du risque en cours
        riderIncPP=annualPrem*self.agelimite*self.isPremPay()
        riderIncPP2=annualPrem*self.agelimite
        precPP=(self.p['PMBREC'] + self.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        frek=self.frac()

        for i in range(1,pol.shape[1]):
    
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
            
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*pol.nbrPolIf
        mathresIF=provMathIf
        mathResIfcorr=pol.zero()       
        mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]        
        reserve=mathResIfcorr
        reserve=np.maximum(reserve,0)
        
        return reserve
 
#Retourne le total des claim pour l'hospitalisation par maladie (RIDERC_OUTGO)
    def claimHospiHealth(self):
        
        annualPrem = (self.p['POLPRVIEHT']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()
        
        return self.hospi() * annualPrem * self.nbrPolIfSM * self.isPremPay()

#Retourne le total des claim pour l'hospitalisation par accident (RIDERC_OUTGO)
    def claimHospiAccident(self):
        
        annualPrem = (self.p['POLPRCPL2']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()
        
        return self.hospi() * annualPrem * self.nbrPolIfSM * self.isPremPay()

#Retourne le total des claim pour la garantie hospitalisation par maladie
    def claimPrincipal(self):
        return self.claimHospiHealth()

#Retourne le total des claim pour les garanties hospitalisation par accident
    def claimCompl(self):
        return self.claimHospiAccident() 



print("Class HO--- %s sec" %'%.2f'%  (time.time() - start_time))




##############################################################################################################################
#Création de la class Preciso et Preciso Plus
############################################################################################################################

class PRECI(Portfolio):
    mods=[25,26]
    ageLimite = 65
    # complPremium=pol.p['POLPRCPL2']

    
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
        prem=pol.p['POLPRVIEHT']
        return prem.to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
    
#Retourne les primes des garanties complémentaires    
    def premiumPrincipal(self):
        return self.purePremium()*self.nbrPolIfSM


#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):

  # Age limite pour hospitalis
        self.agelimite=((self.age()-1)<=self.ageLimite)
           
        annualPrem = (self.p['POLPRVIEHT']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()   
        riderC =  annualPrem * self.isPremPay() *self.dcAccident() * self.nbrPolIfSM
        self.agelimite = self.agelimite * self.one()
        
        #Calcul du risque en cours
        riderIncPP=annualPrem*self.agelimite*self.isPremPay()
        riderIncPP2=annualPrem*self.agelimite
        
# Ne prend pas en compte les risque en cours du modelpoint ??? à modifier (Commence toujours par 0, au lieu des risques en cours actuel)
        # precPP=(self.p['PMBREC'] + self.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        precPP = self.zero()
        frek=self.frac()

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
            
        CaFracPC=self.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        CaPremPC=self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        ppureEnc = (annualPrem * (1-CaPremPC) / CaFracPC)* self.isPremPay() *self.nbrPolIfSM
        
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*self.nbrPolIf
        mathresIF=provMathIf
        
        mathResIfcorr=self.zero()       
        mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]  
        mathResIfcorr = mathResIfcorr - riderC + ppureEnc

        reserve=mathResIfcorr
        reserve=np.maximum(reserve,0)
        
        return reserve
        

#Retourne les sinistres décès 
    def deathClaim(self):  
        capitalCompl = self.p['PMBCAPIT']
        nbDeath=self.nbrDeath
        capitalDC=(self.p['POLPRCPLA']!=0)*capitalCompl
        capital=capitalDC.to_numpy()[:,np.newaxis,np.newaxis]
        return nbDeath*capital


#Retourne les sinistre complémentaire frais de visite       
    def accidentalDeathClaim(self):
     # A MODIFIER 
        self.agelimite=((self.age()-1)<=self.ageLimite)
        claimRate=self.dcAccident()
        premiumPrincipal=self.premiumPrincipal()
        premiumPrincipal=premiumPrincipal*self.agelimite
        claim=claimRate*premiumPrincipal*self.isPremPay()
        
        return claim


#Retourne le total des claim pour la garantie principale    
    def claimPrincipal(self):
        return self.deathClaim()

#Retourne le total des claim pour les garanties complémentaires
    def claimCompl(self):
        return self.accidentalDeathClaim() 


##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################









def tester(self):
    return self

pol = HO()
#pol=FU()
# pol=AX()
#pol=FU(run=[4,5])
# nomat = pol.nbrMaturities
# pol.ids([2142501])
#pol.mod([9])
#pol.modHead([9],2)
# aa = pol.p
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
# q=pol.totalClaim()
#r=pol.totalCommissions()
#s=pol.totalExpense()
t=pol.BEL()

bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()


monCas=t

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)




# aa.to_excel("check portefeuille.xlsx", header = True )




