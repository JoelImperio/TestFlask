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

    
class PRECI(Portfolio):
    mods=[26]

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
        pol.agelimite=((pol.age()-1)<=65)
           
        annualPrem = (pol.p['POLPRVIEHT']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / pol.frac()   
        riderC =  annualPrem * pol.isPremPay() *pol.dcAccident() * pol.nbrPolIfSM
        pol.agelimite = pol.agelimite * pol.one()
        #Calcul du risque en cours
        riderIncPP=annualPrem*pol.agelimite*pol.isPremPay()
        riderIncPP2=annualPrem*pol.agelimite
        
# Ne prend pas en compte les risque en cours du modelpoint ??? à modifier
        # precPP=(pol.p['PMBREC'] + pol.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * pol.one()
        precPP = pol.zero()
        frek=pol.frac()

        for i in range(1,pol.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
            
        CaFracPC=pol.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        CaPremPC=pol.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        ppureEnc = (annualPrem * (1-CaPremPC) / CaFracPC)* pol.isPremPay() *pol.nbrPolIfSM
        
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*pol.nbrPolIf
        mathresIF=provMathIf
        
        mathResIfcorr=pol.zero()       
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
        self.agelimite=((pol.age()-1)<=65)
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




#

##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self

pol = PRECI()
# pol = HO()
#pol=AX()
#pol=AX(run=[4,5])

# pol.ids([269503])
#pol.mod([70])
#pol.modHead([70],2)
aa = pol.p
# cc= pol.accidentalDeathClaim()
a=pol.nbrPolIf
# b=pol.nbrPolIfSM
#c=pol.nbrMaturities
# d=pol.nbrDeath
#e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.purePremium()
# h=pol.deathClaim()
#i=pol.fraisVisiteClaim()
#j=pol.timeBeforeNextPay()
#k=pol.risqueEnCour()
# l=pol.adjustedReserve()
# m=pol.reserveExpense()
# n=pol.unitExpense()
# o=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()
#u=pol.polTermM
# t = pol.claimCompl()
# tt = pol.adjustedReserve()
# bel=np.sum(pol.BEL(), axis=0)
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

aa.to_excel("check portefeuille.xlsx", header = True )
#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])
