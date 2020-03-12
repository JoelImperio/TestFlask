from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
from MyPyliferisk.mortalitytables import *
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
#Création de la class TEMP
##############################################################################################################################

    # Modalité 3 uniquement pour les 1 tête
class TE(Portfolio):
    # mods=[3]
    modHeads = [3],1
    # complPremium=pol.p['POLPRCPL2']

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.modHead([3],1)
        
        
    
#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()
        
    
    
# #  Retourne un vecteur de temps t (représente t dans prophet)
        
#     def time(self):
        
#         increment = np.cumsum(self.one(), axis = 1) -1
        
#         return increment
        
    
    
    
# # Vecteur qui met des 1 tout les 12 mois, sinon 0
#     def isVal(self):
        
#         check = (((self.time()%12))==11)
    
#         return check
    
    
    
#     def rep(self):
        
#         array = np.arange(self.p['Age1AtEntry'], pol.shape[1])
    
#         return array
    
      
    
#   # vecteur calcul valuation l
    
#     def l_val(self):
        
#         annValNQ = (1-self.qx(table=GKM95))*self.isVal()
        
#         return annValNQ
    
    
# #Retourne les primes pures   
#     def purePremium(self):
#         prem=pol.p['POLPRVIEHT']
#         return prem.to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
# #Retourne les primes des garanties complémentaires    
#     def premiumPrincipal(self):
        
#         return (pol.p['POLPRCPL1']+pol.p['POLPRCPL2']+pol.p['POLPRCPL3']+pol.p['POLPRCPL4']+pol.p['POLPRCPL5']+pol.p['POLPRCPL6']+pol.p['POLPRCPLA'] ).to_numpy()[:,np.newaxis,np.newaxis]



#     def adjustedReserve(self):

#   # Age limite pour mod3
#         pol.agelimite=((pol.age()-1)<=60)
           
#         annualPrem = pol.premiumPrincipal()
#         annualPrem = annualPrem / pol.frac()   
#         riderC =  annualPrem * pol.isPremPay() *pol.dcAccident() * pol.nbrPolIfSM
#         pol.agelimite = pol.agelimite * pol.one()
#         #Calcul du risque en cours
#         riderIncPP=annualPrem*pol.agelimite*pol.isPremPay()
#         riderIncPP2=annualPrem*pol.agelimite
        
# # Ne prend pas en compte les risque en cours du modelpoint ??? à modifier
#         # precPP=(pol.p['PMBREC'] + pol.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * pol.one()
#         precPP = pol.zero()
#         frek=pol.frac()

#         for i in range(1,pol.shape[1]):
#             precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
            
#         CaFracPC=pol.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
#         CaPremPC=pol.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
#         ppureEnc = (annualPrem * (1-CaPremPC) / CaFracPC)* pol.isPremPay() *pol.nbrPolIfSM
        
#         mathResBA=np.maximum(precPP,0)
#         mathResPP=mathResBA 
#         provMathIf=mathResPP*pol.nbrPolIf
#         mathresIF=provMathIf
        
#         mathResIfcorr=pol.zero()       
#         mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]  
#         mathResIfcorr = mathResIfcorr - riderC + ppureEnc

#         reserve=mathResIfcorr
#         reserve=np.maximum(reserve,0)
        
#         return reserve
        

    
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self

pol = TE()



monCas=pol.pbAcquAPPUP

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)




# pol.ids([605701, 532301])
# matougto = pol.matOutgo()
# benpp = pol.matBenPP
# nomat = pol.noMats
# pupmat = pol.pupMatbPP
# nopupmat = pol.noPupMat
# surrOutgo = pol.surrOutgo()
# eppAcquAPPUP = pol.eppAcquAPPUP
# pbAcquAPPUP = pol.pbAcquAPPUP
# riderincpp = pol.riderCostPP()
# totclaim = pol.totalClaim()
# protectionavenir = pol.capPA()
# provtechIf = pol.provTechIf()
# adjMathRes2 = pol.adjMathRes2
# provMathAj = pol.provMathAj
# oTaxblInc=pol.oTaxblInc
# totalExpense = pol.totalExpense()
# resfin = pol.rfinAnn
# resfinmois = pol.resFinMois
# resReldMat = pol.resReldMat
# matoutgo = pol.matOutgo()
# provmathif = pol.provMathIf()
# provtechAj = pol.provTechAj()
# riecostoutgo = pol.riderCOutgo()
# provmathAj = pol.provMathAj()
# testt = pol.test()
# mathresBA = pol.mathresBA()
# nopupif = pol.nbrPupsIf
# nomat = pol.noMats
# nonvewred = pol.nbrNewRed
# epAcquAVPUP = pol.epAcquAVPUP
# eppAcquAPPUP33 = pol.eppAcquAPPUP
# pupEben = pol.pbAcqu()
# deathbenef = pol.deathClaim()
# pupdthbPP = pol.pupDeath()
# pbAcquAVPUP = pol.pbAcquAVPUP
# pbacquAPPUP = pol.pbAcquAPPUP
# deathpup=pol.nbrPupDeath
# epargneacquise = pol.epargAcqu()
# pbacquPP= pol.pbAcquPP
# eparPB = pol.eparPB()
# check = pol.ppurePP()
# check2 = pol.prEncInvPP()
# epp = pol.epargAcqu()
# pbb = pol.pbAcqu()
# pol = HO()
#pol=AX()
#pol=AX(run=[4,5])
# chck = pol.isVal()
# adjustRES = pol.adjustedReserve()
#pol.mod([70])
# pol.modHead([3],1)
# aa = pol.p
# cc= pol.accidentalDeathClaim()
# oo = pol.nbrNewPups
# a=pol.nbrPolIf
# b=pol.nbrPolIfSM
#c=pol.nbrMaturities
# d=pol.nbrDeath
# e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.purePremium()
# h=pol.deathClaim()
#i=pol.fraisVisiteClaim()
#j=pol.timeBeforeNextPay()
#k=pol.risqueEnCour()
# l=pol.adjustedReserve()
# m=pol.reserveExpense()
# n=pol.unitExpenseRed()
# o=pol.totalPremium()
q=pol.deathClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()
#u=pol.polTermM
# t = pol.claimCompl()
# tt = pol.adjustedReserve()
# bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()
# ll = pol.l_val()
# nn = pol.nbrNewRed
# pupbenPPP = pol.pupBenPP
print("Class TE--- %s sec" %'%.2f'%  (time.time() - start_time))

 # pol.p=pol.modHead(pol.modHeads)

iii = pol.eppAcquAPPUP


##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################

def testerCas(self):
    return self
# iii = pol.totalPrem()
monCas=q
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)

ss = pol.p
ss.to_excel("check portefeuille.xlsx", header = True )
#Visualiser une dimension d'un numpy qui n'apparait pas
# test = pol.reduction()
# data=pupEben
# a=pd.DataFrame(data[:,:,0])
