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

    
class HO(Portfolio):
    mods=[58]
    # complPremium=pol.p['POLPRCPL2']

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        
    # Age limite pour hospitalis
        self.agelimite=(self.age()-1<=75)

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()








#Retourne le total des claim pour les garanties complémentaires (RIDERC_OUTGO)
    def claimCompl(self):
        
        annualPrem = (self.p['POLPRVIEHT'] + self.p['POLPRCPL2']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()
        return self.hospi() * annualPrem * self.nbrPolIfSM * self.isPremPay()


#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):

        annualPrem = (self.p['POLPRVIEHT'] + self.p['POLPRCPL2']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()
        
        riderC = self.hospi() * annualPrem * self.nbrPolIfSM
        
        
        #Calcul du risque en cours
        riderIncPP=self.claimCompl()*self.agelimite
        riderIncPP2=riderC*self.agelimite
        precPP=(self.p['PMBREC'] + self.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        frek=self.frac()
 

        for i in range(1,self.shape[1]):
        
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
                   
        mathResBA=np.maximum(precPP,0)
        mathResPP=mathResBA 
        provMathIf=mathResPP*self.nbrPolIf
        mathresIF=provMathIf
        
        mathResIfcorr=self.zero()       
        mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]        
        
        # #Primes pure encaissées
        # annPremPP=self.p['POLPRVIEHT'].to_numpy()[:,np.newaxis,np.newaxis]
        # CaFracPC=self.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        # CaPremPC=self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        # prInventPP=(annPremPP*(1-CaPremPC))/CaFracPC
        # prPurePP=prInventPP
        # ppEncPP=(prPurePP/self.frac())*self.isPremPay()
        # pPureEnc=ppEncPP*self.nbrPolIfSM
        
           
        # #Sortie pour les claim principaux
        # riderCostOutgo=self.premiumPrincipal()*self.dcAccident()*self.isPremPay()*self.agelimite
        

        reserve=mathResIfcorr
        reserve=np.maximum(reserve,0)
        
        return reserve
    
    

    def totalClaim(self):
        return self.claimCompl()

##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self


pol = HO()
#pol=AX()
#pol=AX(run=[4,5])

# pol.ids([65905])
#pol.mod([70])
#pol.modHead([70],2)
# aa = pol.p
# a=pol.nbrPolIf
# b=pol.nbrPolIfSM
#c=pol.nbrMaturities
# d=pol.nbrDeath
#e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.purePremium()
#h=pol.deathClaim()
#i=pol.fraisVisiteClaim()
#j=pol.timeBeforeNextPay()
#k=pol.risqueEnCour()
#l=pol.adjustedReserve()
# m=pol.reserveExpense()
#n=pol.unitExpense()
# o=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
#t=pol.BEL()
#u=pol.polTermM
# t = pol.claimCompl()
tt = pol.adjustedReserve()
#bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()



print("Class X--- %s sec" %'%.2f'%  (time.time() - start_time))






##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self

monCas=tt

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)

# aa.to_excel("check portefeuille.xlsx", header = True )
#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])
