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
        self.pbAcqu()
        self.epargnAcqu()

#Cette Loop renvoie l'ensemble des variables récusrives pour les produits épargnes
    def loopSaving(self):

#Variables des actifs            
        nbrPolIf=self.one()
        nbrPolIfSM=self.zero()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrNewRed = self.zero()
        matRate=self.zero()
        
#Variables des réduites
        nbrPupsIf=self.zero()
        nbrPupDeath=self.zero()
        nbrPupSurrender=self.zero()
        nbrPupIfSM=self.zero()
        nbrPupMaturities=self.zero()

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
            
            nbrNewRed[:,i,:] = (nbrPolIf[:,i-1,:] - nbrDeath[:,i,:] - nbrSurrender[:,i,:] - nbrMaturities[:,i,:]) * reduction[:,i,:]
            
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]- nbrNewRed[:,i,:] - nbrMaturities[:,i,:]

#Définition des variables des réduites
            nbrPupMaturities[:,i,:]=nbrPupsIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPupIfSM[:,i,:]=nbrPupsIf[:,i-1,:] - nbrPupMaturities[:,i,:]
            
            nbrPupDeath[:,i,:]=nbrPupIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseTiming*lapse[:,i,:]))
            
            nbrPupSurrender[:,i,:]=nbrPupIfSM[:,i,:]*lapse[:,i,:]*(1-(lapseTiming*qxy[:,i,:]))
            
            nbrPupsIf[:,i,:]=nbrPupsIf[:,i-1,:]-nbrPupDeath[:,i,:]-nbrPupSurrender[:,i,:] - nbrPupMaturities[:,i,:] + nbrNewRed[:,i,:]
      
    
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
        
#Sauvegarde des variables des réduites
        
        #Nombre de polices réduites                                
        self.nbrPupsIf=nbrPupsIf
        #Nombre de police réduites en déduisant les échéances du mois
        self.nbrPupIfSM=nbrPupIfSM
        #Nombre de décès de polices résuites
        self.nbrPupDeath=nbrPupDeath
        #Nombre d'annulation de contrat de polices réduites
        self.nbrPupSurrender=nbrPupSurrender
        # Nombre de police réduite arrivant à maturité
        self.nbrPupMat = nbrPupMaturities
      
        return self

# Ici se trouve la projection des primes dans le futur en tenant compte de l'indexation
    def annualPremium(self):
        
        txIndex = (self.p['POLINDEX'].to_numpy()[:,np.newaxis,np.newaxis]/100) * self.one()
       

        premAnn = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        annualPremium = premAnn * (1 + txIndex)**self.time()
        
        return  annualPremium

# Créer un vecteur de temporel en année depuis le début de la projection qui dépend du duration if
    def time(self):
        
        durif = self.p['DurationIfInitial'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()-1
        durif = np.remainder(durif, 12)
        increment = np.cumsum(self.one(), axis = 1) -1 + durif
        increment = increment/12
        increment = np.floor(increment)
        
        return increment
 
    def deathClaim(self):
        
        addSumAssuree = self.p['POLCAPAUT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        deathBenefit = self.pbAcquPP + self.epargAcqu() + addSumAssuree
        
        deathClaim = deathBenefit * self.nbrDeath + self.pupDeath() * self.nbrPupDeath
        
        return deathClaim

#Calcul de l'épargne acquise par police hors PB
    def epargAcqu(self):
        
        initEpargne = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]
        epargnAcquPP = self.zero()
        epargnAcquPP[:,0,:] = initEpargne
        prEncInv = self.prEncInvPP()
    
    # taux interet mensualisé
        txInteret = self.txInt()
        
    # loop de l'épargne acquise par police, (epargne acquise t-1 + prime investie capitalisé au taux d'intêret)
        for i in range(1,self.shape[1]):
        
            epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]
            
        return epargnAcquPP

#Calcul de la prime encaissée investie par police
    def prEncInvPP(self): 
        return self.isPremPay() * self.ppurePP()/self.frac()

#Calcul de la prime pure annuelle  
    def ppurePP(self):

        premRider = self.p['POLPRCPL9'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        #Determine les frais d'acquisition en fonction de l'année du contrat (A CHANGER CAR ON AURA SUREMENT DES CHGT SUR 1 2 ou 3 ANS pour d'autres polices)
        acquisitionLoading = (self.durationIf()<=12) * self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        annPrem = self.annualPremium()
        gestionLoading = self.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        ppure = (annPrem -  premRider)*(1-gestionLoading -acquisitionLoading )
        return ppure

# benefice en cas de mort d'une police réduite
        
    def pupDeath(self):
        return np.nan_to_num(self.epAcquAVPUP + self.pbAcquAVPUP)

#  PB acquise depuis le début du contrat
    def pbAcqu(self):
        
        pupBBenPP = self.zero()
        initPB = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pupBBenPP[:,0,:] = initPB
        pbAcquAVPUP = self.zero()
        pbAcquAPPUP =self.zero()
        
        # taux interet mensualisé
        txInteret = self.txInt()
        noPupsIf = self.nbrPupsIf
        noNewPups = self.nbrNewRed
        
        #  Possibilité de peut-être le faire sans loop (A VERIFIER)
        for i in range(1,self.shape[1]):
        
            pupBBenPP[:,i,:] = pupBBenPP[:,i-1,:] * txInteret[:,i,:]
            
            pbAcquAVPUP[:,i,:] = pbAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
            a=pbAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBBenPP[:,i,:] * noNewPups[:,i,:]
            b=noPupsIf[:,i,:]
            pbAcquAPPUP[:,i,:] = np.divide(a,b,out=np.zeros_like(a), where=b!=0) 
            
# DIVISION PAR 0 A REGLER !!!!
            
            
            # pbAcquAPPUP[:,i,:] = np.nan_to_num((pbAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBBenPP[:,i,:] * noNewPups[:,i,:]) / noPupsIf[:,i,:])
                 
  
    #Définition des variables récursives
        # PB acquise par police AVANT nouvelle réduction                                 
        self.pbAcquAVPUP=pbAcquAVPUP
        # PB acquise par police APRES nouvelle réduction 
        self.pbAcquAPPUP=pbAcquAPPUP
        # PB acquise
        self.pbAcquPP = pupBBenPP

# epargne acquise par police réduite APRES/AVANT nouvelles réductions
    def epargnAcqu(self):
        
        eppAcquAPPUP = self.zero()
        noPupsIf = self.nbrPupsIf
        noNewPups = self.nbrNewRed
        epAcquAVPUP = self.zero()
        txInteret = self.txInt()
        pupBenPP =self.epargAcqu()
        
        for i in range(1,self.shape[1]):
            
            epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
            a=epAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBenPP[:,i,:] * noNewPups[:,i,:]
            b=noPupsIf[:,i,:]
            eppAcquAPPUP[:,i,:]=np.divide(a,b,out=np.zeros_like(a), where=b!=0) 
            
            
 # DIVISION PAR 0 A REGLER !!!!           
            # eppAcquAPPUP[:,i,:] = np.nan_to_num((epAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBenPP[:,i,:] * noNewPups[:,i,:]) / noPupsIf[:,i,:])

   #Définition des variables récursives
        #Epargne acquise par police AVANT nouvelle réduction                                 
        self.epAcquAVPUP=epAcquAVPUP
        #Epargne acquise par police APRES nouvelle réduction 
        self.eppAcquAPPUP=eppAcquAPPUP
        
        self.pupBenPP = pupBenPP

#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        return self.zero()

#Retourne les claims des garanties complémentaires (RIDERC_OUTGO)
    def claimCompl(self):
        return self.zero()

#Retourne les rachats totaux (SURR_OUTGO)
    def surrender(self):
        return self.zero()

#Retourne les échéances (MAT_OUTGO)
    def maturity(self):
        return self.zero()



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
# pol.ids([515503,1736301,1900401,2168101,2396001,2500001,2500101,2466301])

pol.mod([28])
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
# o=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()

# bel=np.sum(pol.BEL(), axis=0)
# pgg=pol.PGG()

gg=pol.deathClaim()


print("Class EP--- %s sec" %'%.2f'%  (time.time() - start_time))

monCas=gg

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



