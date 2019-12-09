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
class TEMP(Portfolio):
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
        






    # Modalité 28 
class EPP28(Portfolio):
    mods=[28]
    addSumAssuree = 7500
    premDCmaladie = 48

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)


#Permet de relancer l'update() en intégrant des methodes de la sous-classe (ICI la loop inforce possède la possibilité de réduction)
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopSaving()
        self.loopReduction()
        self.epargnAcqu()
        self.pbAcqu()

# Créer un vecteur de temporel en année depuis le début de la projection qui dépend du duration if
    def time(self):
        
        durif = self.p['DurationIfInitial'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()-1
        durif = np.remainder(durif, 12)
        increment = np.cumsum(self.one(), axis = 1) -1 + durif
        increment = increment/12
        increment = np.floor(increment)
        
        return increment
    
    
# Créer un vecteur correspondans a calendar_month dans prophet (le mois de la projection)
    def calendarMonth(self):
        
        increment = np.cumsum(self.one(), axis = 1) -2
        increment = increment%12 +1
        # increment[:,0,:] = 12
        return increment
    
    
    


# Ici se trouve la projection des primes dans le futur en tenant compte de l'indexation
    def premIndex(self):
        
        txIndex = (self.p['POLINDEX'].to_numpy()[:,np.newaxis,np.newaxis]/100) * self.one()
       
        # Les primes sont forcées à 0 lorsque la police est réduite
        mask = (self.p['POLSIT']==9)|(self.p['POLSIT']==4)|(self.p['PMBFRACT']==0)|(self.p['PMBFRACT']==5)
        premAnn = self.p['POLPRTOT'] * (1-mask)
        premAnn = premAnn.to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        premIndex = premAnn * (1 + txIndex)**self.time()
        
        return  premIndex


#  Vecteur des primes total
    def totalPrem(self):
        
        totPrem = self.isPremPay() * self.premIndex() * self.nbrPolIfSM/self.frac()
        return totPrem



# Calcul de la prime pure annuelle  
    def ppurePP(self):
        
        
       #  Condition qui met des primes à 0 pour des fractionnements 5 ou 0 et polices réduite
        mask = (self.p['POLSIT']==9)|(self.p['POLSIT']==4)|(self.p['PMBFRACT']==0)|(self.p['PMBFRACT']==5)
        premRider = (self.p['POLPRCPL9']) * (1-mask)
        premRider = premRider.to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        # Determine les frais d'acquisition en fonction de l'année du contrat (A CHANGER CAR ON AURA SUREMENT DES CHGT SUR 1 2 ou 3 ANS pour d'autres polices)
        acquisitionLoading = (self.durationIf()<=12) * self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        annPrem = self.premIndex()
        gestionLoading = self.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        ppure = (annPrem -  premRider)*(1-gestionLoading -acquisitionLoading )
        return ppure
    
    
#  calcul de la prime encaissée investie par police
    def prEncInvPP(self):
        
        return self.isPremPay() * self.ppurePP()/self.frac()


#  taux d'intêret mensualisé
    def txInt(self):
        txInteret = ((1+self.p['POLINTERG']/100)**(1/12)).to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        return txInteret



#  calcul de l'épargne acquise par police hors PB
    def epargAcqu(self):
        
        initEpargne = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]
        epargnAcquPP = self.zero()
        epargnAcquPP[:,0,:] = initEpargne
        prEncInv = self.prEncInvPP()
    # taux interet mensualisé
        txInteret = self.txInt()
        
        for i in range(1,self.shape[1]):
        
            epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]
            
        return epargnAcquPP
    
    
    
#  PB acquise depuis le début du contrat
    def pbAcqu(self):
    
        initPB = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pupBBenPP = self.zero()
        pupBBenPP[:,0,:] = initPB
        pbAcquAVPUP = self.zero()
        pbAcquAPPUP =self.zero()
        # taux interet mensualisé
        txInteret = self.txInt()
        noPupsIf = self.nbrPupsIf
        noNewPups = self.nbrNewRed
        
        #  Possibilité de le faire sans loop (A VERIFIER)
        for i in range(1,self.shape[1]):
        
            pupBBenPP[:,i,:] = pupBBenPP[:,i-1,:] * txInteret[:,i,:]
            
            pbAcquAVPUP[:,i,:] = pbAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
            pbAcquAPPUP[:,i,:] = np.nan_to_num((pbAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBBenPP[:,i,:] * noNewPups[:,i,:]) / noPupsIf[:,i,:])
            # pbAcquAPPUP[:,i,:][noPupsIf[:,i,:] == 0] = zero[:,i,:]
            
        #Définition des variables récursives
        #pb acquise par police AVANT nouvelle réduction                                 
        self.pbAcquAVPUP=pbAcquAVPUP
        #PB acquise par police APRES nouvelle réduction 
        self.pbAcquAPPUP=pbAcquAPPUP
        # PB acquise
        self.pbAcquPP = pupBBenPP







# epargne acquise par police réduite APRES/AVANT nouvelles réductions
    # @property
    def epargnAcqu(self):
        
        eppAcquAPPUP = self.zero()
        noPupsIf = self.nbrPupsIf
        noNewPups = self.nbrNewRed
        epAcquAVPUP = self.zero()
        txInteret = self.txInt()
        pupBenPP =self.epargAcqu()
        
        for i in range(1,self.shape[1]):
            
            epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
            eppAcquAPPUP[:,i,:] = np.nan_to_num((epAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBenPP[:,i,:] * noNewPups[:,i,:]) / noPupsIf[:,i,:])
           
        
        
        
    #Définition des variables récursives
        #Epargne acquise par police AVANT nouvelle réduction                                 
        self.epAcquAVPUP=epAcquAVPUP
        #Epargne acquise par police APRES nouvelle réduction 
        self.eppAcquAPPUP=eppAcquAPPUP
        
        self.pupBenPP = pupBenPP


        
# benefice en cas de mort d'une police réduite
        
    def pupDeath(self):
        return np.nan_to_num(self.epAcquAVPUP + self.pbAcquAVPUP)
    



#  epargne et PB calculée au taux de PB
        
    # def eparPB(self):
        
    #     txIntAnn = self.p['POLINTERG'].to_numpy()[:,np.newaxis, np.newaxis] * self.one()/100
    #     initPB = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
    #     initEpargne = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]
        
    #     eparPB = self.zero()
    #     eparPB[:,0,:] = initPB + initEpargne
        
    #     calendarMonth = self.calendarMonth()
        
    #     for i in range(1,self.shape[1]):
    #         # eparPB[:,i,:] = eparPB[:,i-1,:] * (1 + txIntAnn[:,i,:])/(1+ txIntAnn[:,i,:]**(((12 - (12-calendarMonth[:,i,:])%12 ))/12))
    #         eparPB[:,i,:] = eparPB[:,i-1,:] * (1 + txIntAnn[:,i,:])**(calendarMonth/12)

    #     return eparPB



# benefit en cas de mort (DEATH_OUTGO)
    def deathClaim(self):
        
        deathBenefit = self.pbAcquPP + self.epargAcqu() + self.addSumAssuree
        
        deathClaim = deathBenefit * self.nbrDeath + self.pupDeath() * self.nbrPupDeath
        
        return np.nan_to_num(deathClaim)

    
    
    
    
    def mathresBA(self):

        return self.epargAcqu() + self.pbAcquPP
    
    
    
#  benefit en cas d'annulation (SURR_OUTGO)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def test(self):
        

    
        return self.pbAcquPP + self.epargAcqu() + self.addSumAssuree
    
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self

pol = EPP28()
# pol.ids([1023002])
testt = pol.test()
# nopupif = pol.nbrPupsIf
# nonvewred = pol.nbrNewRed
# epAcquAVPUP = pol.epAcquAVPUP
# eppAcquAPPUP33 = pol.eppAcquAPPUP
# pupEben = pol.pbAcqu()
deathbenef = pol.deathClaim()
# pupdthbPP = pol.pupDeath()
# pbAcquAVPUP = pol.pbAcquAVPUP
# pbacquAPPUP = pol.pbAcquAPPUP
# deathpup=pol.nbrPupDeath
epargneacquise = pol.epargAcqu()
pbacquPP= pol.pbAcquPP
# eparPB = pol.eparPB()
# check = pol.ppurePP()
# check2 = pol.prEncInvPP()
# epp = pol.epargAcqu()
# pbb = pol.pbAcqu()
# pol = HO()
#pol=AX()
#pol=AX(run=[4,5])
# chck = pol.isVal()

#pol.mod([70])
# pol.modHead([3],1)
# aa = pol.p
# cc= pol.accidentalDeathClaim()
# oo = pol.nbrNewPups
a=pol.nbrPolIf
# b=pol.nbrPolIfSM
#c=pol.nbrMaturities
d=pol.nbrDeath
e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.purePremium()
# h=pol.deathClaim()
#i=pol.fraisVisiteClaim()
#j=pol.timeBeforeNextPay()
#k=pol.risqueEnCour()
# l=pol.adjustedReserve()
# m=pol.reserveExpense()
# n=pol.unitExpense()
o=pol.totalPrem()
# q=pol.totalClaim()
r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()
#u=pol.polTermM
# t = pol.claimCompl()
# tt = pol.adjustedReserve()
# bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()
# ll = pol.l_val()
nn = pol.nbrNewRed
pupbenPPP = pol.pupBenPP
print("Class X--- %s sec" %'%.2f'%  (time.time() - start_time))

 # pol.p=pol.modHead(pol.modHeads)

iii = pol.eppAcquAPPUP


##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self
# iii = pol.totalPrem()
monCas=deathbenef
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)

ss = pol.p
ss.to_excel("check portefeuille.xlsx", header = True )
#Visualiser une dimension d'un numpy qui n'apparait pas
test = pol.reduction()
# data=pupEben
# a=pd.DataFrame(data[:,:,0])
