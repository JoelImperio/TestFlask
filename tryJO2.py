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
    ageLimite = 75    

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopSaving()

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

#Variables de l'épargne actifs et réduits
        epargnAcquPP = self.zero()        
        eppAcquAPPUP = self.zero()
        epAcquAVPUP = self.zero()

        epargnAcquPP[:,0,:] = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]        


#Variables de PB actifs et réduites
 # --- A SUPPRIMER   pupBBenPP = self.zero()
        pbAcquAVPUP = self.zero()
        pbAcquAPPUP =self.zero()
        
 # --- A SUPPRIMER   pupBBenPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
      
        
        
        
        
# --- AJOUT JO
        pbIncorPUP = self.zero()
        
        epgTxPB_PUP = self.zero()
        epgTxPB_PUP[:,0,:] = 0
        
        pbCalcPUP = self.zero()
        allocMonths = self.allocMonths()
        
        # Taux annualisé
        txIntPC = self.txInt()**(12) - 1

        txPbPC = self.txPbPC()/100
        
        # taux annualisé
        txIntPC = self.txInt()**(12) - 1
        epgTxPB_PP = self.epgTxPB_PP()
        
        txTot = 1 + (txPbPC + txIntPC)
        
        pbIncorPP = self.zero()
        pbAcquPP = self.zero()
        pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pbCalcPP = self.zero()
        isActive = self.isActive()
        
        
        
        
        
        
        
        
#Variables biométriques et génériques
        lapseTiming=0.5
        polTermM=self.polTermM()       
        lapseD=lapseTiming * self.lapse()
        lapse = self.lapse()        
        reduction = self.reduction()       
        qxy=self.qxyExpMens()
        qxyD =lapseTiming * self.qxyExpMens()
        txInteret = self.txInt()
        prEncInv = self.premiumInvested()
        
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

#Définition des variables d'épargne pour actives et réduites
            epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]

            epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
            epTemp=epAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + epargnAcquPP[:,i,:] * nbrNewRed[:,i,:]
            
            eppAcquAPPUP[:,i,:]=np.divide(epTemp,nbrPupsIf[:,i,:],out=np.zeros_like(epTemp), where=nbrPupsIf[:,i,:]!=0)


            
# --- AJOUT JO  
            
            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:])
            
            pbIncorPUP[:,i,:] = np.nan_to_num(pbCalcPUP[:,i-1,:])
         
            pbAcquAVPUP[:,i,:] = (pbAcquAPPUP[:,i-1,:] + pbIncorPUP[:,i,:]) * txInteret[:,i,:]

            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:]) * txInteret[:,i,:] * isActive[:,i,:]
           
            
            
            #Définition des variables de PB pour actives et réduites
# --- A SUPPRIMER     pupBBenPP[:,i,:] = (pupBBenPP[:,i-1,:]) * txInteret[:,i,:]
        
            

            pbTemp=pbAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + pbAcquPP[:,i,:] * nbrNewRed[:,i,:]            
            
            pbAcquAPPUP[:,i,:] = np.divide(pbTemp,nbrPupsIf[:,i,:],out=np.zeros_like(pbTemp), where=nbrPupsIf[:,i,:]!=0)       



# --- AJOUT JO  
            epgTxTEMP = epgTxPB_PUP[:,i-1,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) * (txTot[:,i,:]**(1/12)) + (epgTxPB_PP[:,i,:] *  nbrNewRed[:,i,:])
            
            epgTxPB_PUP[:,i,:] =  np.divide(epgTxTEMP, nbrPupsIf[:,i,:], out=np.zeros_like(epgTxTEMP), where=nbrPupsIf[:,i,:]!=0)
               
            pbCalcPP[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0) * allocMonths[:,i,:] * isActive[:,i,:]
            
            pbCalcPUP[:,i,:] = np.maximum((epgTxPB_PUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * allocMonths[:,i,:] * isActive[:,i,:]

  
 

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

#Sauvegarde des variables d'éparnge actifs et réduites
        
        #Epargne acquise par police AVANT nouvelle réduction                                 
        self.epAcquAVPUP=epAcquAVPUP
        #Epargne acquise par police APRES nouvelle réduction 
        self.eppAcquAPPUP=eppAcquAPPUP
        #Epargne aquise des polices actives
        self.epargnAcquPP = epargnAcquPP


#Sauvgarde des variables de  PB pour actives et réduites
# ---A MODIFIER JO
        # PB acquise par police AVANT nouvelle réduction                                 
        self.pbAcquAVPUP=np.nan_to_num(pbAcquAVPUP)
        # PB acquise par police APRES nouvelle réduction 
        self.pbAcquAPPUP=np.nan_to_num(pbAcquAPPUP)
        # PB acquise des polices actives
# --- A SUPPRIMER   self.pbAcquPP = pupBBenPP      
        

# --- AJOUT JO
        #  PB à affecter par police réduite
        self.pbCalcPUP = pbCalcPUP
        # epargne et PB des polices réduites calculé au taux PB
        self.epgTxPB_PUP = epgTxPB_PUP
        # PB incorporée par contrat réduit
        self.pbIncorPUP = pbIncorPUP
        # Montant de PB à affecter par police
        self.pbCalcPP = pbCalcPP
        # PB acquise des polices actives
        self.pbAcquPP = pbAcquPP
        # PB incorporée par police
        self.pbIncorPP = pbIncorPP
        # PB incorporée par police réduite
        self.pbIncorPUP = pbIncorPUP
        
        
        return

#Retourne les primes commerciales annuel  avec indexation
    def premiumAnnual(self):
        
        txIndex = (self.p['POLINDEX'].to_numpy()[:,np.newaxis,np.newaxis]/100) * self.one()
       
        premAnn = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        return  premAnn * (1 + txIndex)**self.projectionYear()
    
#Retourne les primes complémentaires commerciales annuelles
    def premiumCompl(self):     
        
        riderPremium=self.p['POLPRCPL9'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()     
        
        return riderPremium

#Retourne les primes pures annuelles  
    def premiumPure(self):

        annPrem = self.premiumAnnual()      
        premRider = self.premiumCompl()
  
        #Determine les frais d'acquisition en fonction de l'année du contrat (A CHANGER CAR ON AURA SUREMENT DES CHGT SUR 1 2 ou 3 ANS pour d'autres polices)
        # acquisitionLoading = (self.durationIf()<=12) * self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        acquisitionLoading=self.one()
        acquisitionLoading =acquisitionLoading* (self.durationIf()<=12) * self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        acquisitionLoading =acquisitionLoading* (self.durationIf()<=24) * self.p['aquisitionLoadingYear2'].to_numpy()[:,np.newaxis,np.newaxis]
        acquisitionLoading =acquisitionLoading* (self.durationIf()<=36) * self.p['aquisitionLoadingYear3'].to_numpy()[:,np.newaxis,np.newaxis]
        acquisitionLoading =acquisitionLoading* (self.durationIf()>36) * self.zero()
                     
        gestionLoading = self.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()

        return (annPrem -  premRider)*(1-gestionLoading -acquisitionLoading )

#Retourne les primes investis
    def premiumInvested(self):
        return self.isPremPay() * self.premiumPure()/self.frac()

#Retourn la réserve mathémathique incluant la PB
    def mathresBA(self):

        return  self.epargnAcquPP + self.pbAcquPP + self.riskEnCours()      

#Retourne le risque en cours
    def riskEnCours(self):

        #Age limite pour Epargne
        agelimite=((self.age()-1)<=self.ageLimite)* self.one()

        frek=self.frac()
          
        premCompl =  self.premiumCompl()/frek 
        
        #Calcul du risque en cours
        riderIncPP=premCompl*agelimite*self.isPremPay()
        riderIncPP2=premCompl*agelimite
        
        precPP = self.zero()

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
              
        return precPP

#Retourne les claims décès
    def deathClaim(self):
        
# =============================================================================
#    --- AJOUT JO     
# =============================================================================
        
        
        addSumAssuree = self.p['POLCAPAUT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        mask32 = self.p['PMBMOD'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()  == 32
        
        mask_55 =mask32 & (self.age() <= 55)
        mask_55_65 =mask32 & (self.age() > 55) & (self.age() <= 65)       
        mask_65 =mask32 & (self.age() > 65)

        
        addSumAssuree[mask_55]=30000
        addSumAssuree[mask_55_65]=7500        
        addSumAssuree[mask_65]=2500       
        
        
        mask36 = self.p['PMBMOD'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()  == 36
        addSumAssuree[mask36]=50000
        
        
        deathBenefit = self.pbAcquPP + self.epargnAcquPP + addSumAssuree
        
        deathBenefitReduced=np.nan_to_num(self.epAcquAVPUP + self.pbAcquAVPUP)
        
        deathClaim = deathBenefit * self.nbrDeath + deathBenefitReduced * self.nbrPupDeath
        

        # pupDeath = np.nan_to_num(self.epAcquAVPUP + self.pbAcquAVPUP)
        
        # deathClaim = deathBenefit * self.nbrDeath + pupDeath * self.nbrPupDeath
        
        
        
        
        
        
        return deathClaim


#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        return self.deathClaim()

#Retourne les claims des garanties complémentaires (RIDERC_OUTGO)
    def claimCompl(self):
        return self.zero()

#Retourne les rachats totaux (SURR_OUTGO)
    def surrender(self):
        
        #Rachats des polices active
        surrIf = self.mathresBA() * self.nbrSurrender
        
        #Rachat des polices réduites
        surrRed = (self.pbAcquAPPUP + self.eppAcquAPPUP) * self.nbrPupSurrender        
        
        return surrIf + surrRed

#--- A SUPPRIMER #Retourne les échéances (MAT_OUTGO)
    # def maturity(self):
    #     return self.zero()







# =============================================================================
# --- AJOUT JO 
# =============================================================================



    
# Calcul des sorties dûes aux maturité des polices (MAT_OUTGO)
    def maturity(self):
        
        matBenPP = self.epargnAcquPP + self.pbAcquPP
        noMats = self.nbrNewMat
        pupMatbPP =  self.epAcquAVPUP + self.pbAcquAPPUP
        noPupMat = self.nbrPupMat
   
        matOutgo = self.zero()
        
        for i in range(1,self.shape[1]+1):
            
            matOutgo[:,i,:] = matBenPP[:,i-1,:] * noMats[:,i,:] + pupMatbPP[:,i-1,:] * noPupMat[:,i,:]
           
 #Définition des variables récursives
        self.matBenPP = matBenPP
        self.noMats = noMats
        self.pupMatbPP = pupMatbPP
        self.noPupMat = noPupMat
        
        # return matBenIF + matBenPPUPif
        return matOutgo
    


# Créer un vecteur correspondans a calendar_month dans prophet (le mois de la projection)
    def calendarMonth(self):
        
        increment = np.cumsum(self.one(), axis = 1) -2
        increment = increment%12 +1

        return increment




# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):

        
        mois = self.calendarMonth()
        mask = mois ==12
        
        return mask*1



# Taux de participation aux benefices (TX_PB_PC)
    def txPbPC(self):
        
        pbRate = self.pbRate()
        txInt = (self.txInt()**12) - 1
        txPbPC = pbRate - txInt
        return np.maximum(txPbPC, 0)*100
    
    
    
# Epargne et PB calculée au Taux de PB
    def epgTxPB_PP(self):
        
        premiumInvested = self.premiumInvested()
        txIntPC = self.txInt()**(12) - 1
        epgTxPB_PP = self.one()
        txPB_PC = self.txPbPC()/100
        
        txTot = 1 + (txPB_PC + txIntPC)
        
        epgTxPB_PP[:,0,:] = (self.p['PMBPBEN'] + self.p['PMBPRVMAT']).to_numpy()[:,np.newaxis] 
        
        for i in range(1,self.shape[1]):
        
            epgTxPB_PP[:,i,:] = (epgTxPB_PP[:,i-1,:]  + premiumInvested[:,i,:]) *  (txTot[:,i,:])**(1/12)
        
        return epgTxPB_PP



# Vecteur de 1 et 0 permettant de savoir si police toujours active ou non
    def isActive(self):
        
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        increment = np.cumsum(self.one(), axis = 1) -1

        mask = moisRestant >= increment
        
        return mask














##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################


def tester(self):
    return self

pol = EP()

# a = pol.epgTxPB_PP()


#pol=EP(run=[4,5])
# pol.ids([818801])
# pol.ids([1748802])
# pol.ids([493202, 524401])
# pol.ids([515503,1736301,1900401,2168101,2396001,2500001,2500101,2466301])

pbacqAPVUP = pol.pbAcquAVPUP


pol.mod([36])
#pol.modHead([9],2)
aa = pol.p
#a=pol.nbrPolIf
#b=pol.nbrPolIfSM
#c=pol.nbrMaturities
#d=pol.nbrDeath
#e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.premiumPure()
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

gg=pol.claimPrincipal()


# def premiumPure(self):

annPrem = pol.premiumAnnual()      
premRider = pol.premiumCompl()
  
#Determine les frais d'acquisition en fonction de l'année du contrat (A CHANGER CAR ON AURA SUREMENT DES CHGT SUR 1 2 ou 3 ANS pour d'autres polices)
# acquisitionLoading = (pol.durationIf()<=12) * pol.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * pol.one()
acquisitionLoading=pol.one()
acquisitionLoading =acquisitionLoading* (pol.durationIf()<=12) * pol.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
acquisitionLoading =acquisitionLoading* (pol.durationIf()<=24) * pol.p['aquisitionLoadingYear2'].to_numpy()[:,np.newaxis,np.newaxis]
acquisitionLoading =acquisitionLoading* (pol.durationIf()<=36) * pol.p['aquisitionLoadingYear3'].to_numpy()[:,np.newaxis,np.newaxis]
    
gestionLoading = pol.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * pol.one()

purePremium=(annPrem -  premRider)*(1-gestionLoading -acquisitionLoading )

a=(pol.durationIf()<=24)

### Dans pbAcquAVPUP il manque la variable PB_INCOR_PUP (mod31)
# def deathClaim(self):

addSumAssuree = pol.p['POLCAPAUT'].to_numpy()[:,np.newaxis,np.newaxis] * pol.one()

deathBenefit = pol.pbAcquPP + pol.epargnAcquPP + addSumAssuree

deathBenefitReduced=pol.epAcquAVPUP + pol.pbAcquAVPUP

deathClaim = deathBenefit * pol.nbrDeath + deathBenefitReduced * pol.nbrPupDeath



print("Class EP--- %s sec" %'%.2f'%  (time.time() - start_time))

monCas=pol.deathClaim()

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



