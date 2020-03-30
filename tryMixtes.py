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
#Création de la class Epargne
############################################################################################################################

class MI(Portfolio):
    mods=[2,10,6,7]

#Products: F1XT_1,F2XT_1,F1XT14,F1XT11


    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopEndowment()

#Cette Loop renvoie l'ensemble des variables récusrives pour les produits mixtes
    def loopEndowment(self):

#Variables des actifs            
        nbrPolIf=self.one()
        nbrPolIfSM=self.zero()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrNewRed = self.zero()
        matRate=self.zero()
             
        
#Variables biométriques et génériques
        lapseTiming=0.5
        polTermM=self.polTermM()       
        lapseD=lapseTiming * self.lapse()
        lapse = self.lapse()        
        reduction = self.reduction()       
        qxy=self.qxyExpMens()
        qxyD =lapseTiming * self.qxyExpMens()

        
        #Définition du vecteur des maturités (bool)        
        matRate[polTermM+1 ==self.durationIf()]=1 
            
        for i in range(1,self.shape[1]):

#Définition des variables des actifs            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:] - nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseD[:,i,:]))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxyD[:,i,:]))
            
            # nbrNewRed[:,i,:] = (nbrPolIf[:,i-1,:] - nbrDeath[:,i,:] - nbrSurrender[:,i,:] - nbrMaturities[:,i,:]) * reduction[:,i,:]
            
            # nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]- nbrNewRed[:,i,:] - nbrMaturities[:,i,:]

          
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:] - nbrMaturities[:,i,:]


#Sauvegarde des variables des actifs
       
        #Nombre de polices actives                                 
        self.nbrPolIf=nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM=nbrPolIfSM
        #Nombre de décès
        self.nbrDeath=nbrDeath
        #Nombre d'annulation de contrat
        self.nbrSurrender=nbrSurrender
        #Nombre de nouvelle réduction
        self.nbrNewRed = nbrNewRed
        # Nombre de nouvelle maturités
        self.nbrNewMat = nbrMaturities
             
        
        return

#Retourne les primes totales perçues
    def totalPremium(self):
        premInc=(self.p['POLPRTOT'])[:,np.newaxis,np.newaxis]/self.frac()
           
        prem=premInc*self.nbrPolIfSM*self.isPremPay()*self.indexation()
        
        return prem


#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        return self.zero()

#Retourne les claims des garanties complémentaires (RIDERC_OUTGO)
    def claimCompl(self):
        return self.zero()

#Retourne les rachats totaux (SURR_OUTGO)
    def surrender(self):
        return self.zero()

#Retourne les rachats partiels (PARTSV_OUTGO)
    def partialSurrender(self):
        return self.zero()

#Retourne les échéances (MAT_OUTGO)
    def maturity(self):
        return self.zero()


##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################


def tester(self):
    return self

pol = MI()
#pol=MI(run=[4,5])

    ###  Mod 2_1 produit F1XT1
# pol.ids([301])
# pol.modHead([2],1)

    ### Mod 2_2 F2XT_1
# pol.ids([2501])
# pol.modHead([2],1)

    ### Mod 10 F1XT14
# pol.ids([1602604])
# pol.mod([10])

    ### Mod 6 F1XT11
# pol.ids([799003])
# pol.mod([6,7])


# a = pol.p
# b=pol.nbrPolIf
# c=pol.nbrPolIfSM
# d=pol.nbrNewMat
# e=pol.nbrDeath
# f=pol.nbrSurrender
# g=pol.premiumCompl()
#h=pol.premiumPure()
#i=pol.deathClaim()
#j=pol.fraisVisiteClaim()
#k=pol.timeBeforeNextPay()
#l=pol.risqueEnCour()
# m=pol.adjustedReserve()
#n=pol.reserveExpense()
#o=pol.unitExpense()
p=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()

# bel=np.sum(pol.BEL(), axis=0)
# pgg=pol.PGG()



print("Class MI--- %s sec" %'%.2f'%  (time.time() - start_time))

monCas=p
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



