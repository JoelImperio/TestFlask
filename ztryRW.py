from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import datetime 
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
        self.reserveForExp()

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

        pbAcquAVPUP = self.zero()
        pbAcquAPPUP =self.zero()
        pbIncorPUP = self.zero()      
        epgTxPbPUP = self.zero()
        pbCalcPUP = self.zero()
        pbPupDTHS=self.zero()
        pbSortDTHS=self.zero()
        
        epgTxPbPUP[:,0,:] = 0
        
# --- AJOUT JO
        pbSortMatsPP= self.zero()
        pbSortMatsPUP = self.zero()


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
        
        
        pbCalcPPdths = self.zero()
        pbCalcPUPdths = self.zero()
        
        
        
        
        
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
            
            epTemp = epAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + epargnAcquPP[:,i,:] * nbrNewRed[:,i,:]
            
            eppAcquAPPUP[:,i,:] = np.divide(epTemp,nbrPupsIf[:,i,:],out=np.zeros_like(epTemp), where=nbrPupsIf[:,i,:]!=0)

            

           
            
            
#Définition des variables de PB pour actives et réduites

    ### PB        
            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            pbIncorPUP[:,i,:] = np.nan_to_num(pbCalcPUP[:,i-1,:]  * isActive[:,i-1,:]) 

            pbSortDTHS[:,i,:] = np.nan_to_num(pbCalcPPdths[:,i,:] * isActive[:,i,:]) 
            
            pbPupDTHS[:,i,:] = np.nan_to_num(pbCalcPUPdths[:,i,:] * isActive[:,i,:]) 

         
            pbAcquAVPUP[:,i,:] = (pbAcquAPPUP[:,i-1,:] + pbIncorPUP[:,i,:]) * txInteret[:,i,:]

            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:]) * txInteret[:,i,:] * isActive[:,i,:]            

            pbTemp=pbAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + pbAcquPP[:,i,:] * nbrNewRed[:,i,:]            
            
            pbAcquAPPUP[:,i,:] = np.divide(pbTemp,nbrPupsIf[:,i,:],out=np.zeros_like(pbTemp), where=nbrPupsIf[:,i,:]!=0)       
  
            epgTxTEMP = epgTxPbPUP[:,i-1,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) * (txTot[:,i,:]**(1/12)) + (epgTxPB_PP[:,i,:] *  nbrNewRed[:,i,:])
            
            epgTxPbPUP[:,i,:] =  np.divide(epgTxTEMP, nbrPupsIf[:,i,:], out=np.zeros_like(epgTxTEMP), where=nbrPupsIf[:,i,:]!=0)
               
            pbCalcPP[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0)  * allocMonths[:,i,:]
            
            pbCalcPUP[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * allocMonths[:,i,:]
            
            
            pbCalcPPdths[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
            pbCalcPUPdths[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
            

            pbCalcPPdths[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0)  * (1 - allocMonths[:,i,:]) 
            
            pbCalcPUPdths[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * (1 - allocMonths[:,i,:]) 
 
        
 
            pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
            pbSortMatsPUP[:,i,:] = pbCalcPUP[:,i,:] * isActive[:,i,:]

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
        
        # PB acquise par police AVANT nouvelle réduction                                 
        self.pbAcquAVPUP=np.nan_to_num(pbAcquAVPUP)
        # PB acquise par police APRES nouvelle réduction 
        self.pbAcquAPPUP=np.nan_to_num(pbAcquAPPUP)
        #  PB à affecter par police réduite
        self.pbCalcPUP = pbCalcPUP
        # epargne et PB des polices réduites calculé au taux PB
        self.epgTxPbPUP = epgTxPbPUP
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
        # PB non incorporée des polices réduites
        self.pbPupDTHS=pbPupDTHS
        # PB non incorporée des polices actives
        self.pbSortDTHS=pbSortDTHS
# --- AJOUT JO
        # Pb donnée par police en cas de maturité
        self.pbSortMatsPP = pbSortMatsPP
        # pb donnée par police en cas de maturité d'une police réduite
        self.pbSortMatsPUP = pbSortMatsPUP
        
        # pb donnée par police en cas de décès
        self.pbCalcPPdths = pbCalcPPdths
        # pb donné par police en cas de décès d'une police réduite
        self.pbCalcPUPdths = pbCalcPUPdths
        
        return

#Retourne les primes commerciales annuel  avec indexation
    def premiumAnnual(self):
        
        txIndex = (self.p['POLINDEX'].to_numpy()[:,np.newaxis,np.newaxis]/100) * self.one()
       
        premAnn = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        return  premAnn * (1 + txIndex)**self.projectionYear()
    
#Retourne les primes complémentaires commerciales annuelles
    def premiumCompl(self):     
        
        riderPremium=self.p['POLPRCPL9'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        
        rider33_36=self.p['POLPRCPL3'].to_numpy()[:,np.newaxis,np.newaxis] * self.one() \
            +self.p['POLPRCPL4'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()\
                # +self.p['POLPRCPLA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        

        
        riderPremium[self.mask([33,36])]=riderPremium[self.mask([33,36])]+rider33_36[self.mask([33,36])]
                 
       
        
        
        
        return riderPremium

#Retourne les primes pures annuelles  
    def premiumPure(self):

        annPrem = self.premiumAnnual()      
        premRider = self.premiumCompl()
  
        acquisitionLoading=self.one()
        acquisitionLoading =acquisitionLoading* (self.durationIf()<=12) * self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        acquisitionLoading =acquisitionLoading* (self.durationIf()<=24) * self.p['aquisitionLoadingYear2'].to_numpy()[:,np.newaxis,np.newaxis]
        acquisitionLoading =acquisitionLoading* (self.durationIf()<=36) * self.p['aquisitionLoadingYear3'].to_numpy()[:,np.newaxis,np.newaxis]
        acquisitionLoading =acquisitionLoading* (self.durationIf()>36) * self.zero()
                     
        gestionLoading = self.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()

        return (annPrem -  premRider)*(1-gestionLoading -acquisitionLoading )

#Retourne les primes investis
    def premiumInvested(self):
        
        premInvest = self.isPremPay() * self.premiumPure()/self.frac()
      
        return premInvest

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
        
# --- AJOUT JO
# A rajouté pour corrigé les risque en cours 
        # precPP[:,0,:] = pol.p['PMBREC'].to_numpy()[:,np.newaxis] 

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
              
        return precPP

#Retourne les claims décès
    def deathClaim(self):

        addSumAssuree = self.p['POLCAPAUT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        mask_55 = (self.age() <= 55)
        mask_55_65 = (self.age() > 55) & (self.age() <= 65)       
        mask_65 = (self.age() > 65)
      
        addSumAssuree[(self.mask([32])) & mask_55]=30000
        addSumAssuree[(self.mask([32])) & mask_55_65]=7500        
        addSumAssuree[(self.mask([32])) & mask_65]=2500       
        
        # --- AJOUT JO
        # Il y a des mod 33 avec POLCAPAUT à 0, je les mets tous à 30'000
        addSumAssuree[self.mask([33])]=30000
        
        
        deathBenefit = self.pbAcquPP + self.epargnAcquPP + addSumAssuree + self.pbSortDTHS
        
        deathBenefit[(self.mask([33]))]=np.maximum(deathBenefit[(self.mask([33]))]-addSumAssuree[(self.mask([33]))],addSumAssuree[(self.mask([33]))])
        
        deathBenefitReduced=np.nan_to_num(self.epAcquAVPUP + self.pbAcquAVPUP + self.pbPupDTHS)
        
        deathClaim = deathBenefit * self.nbrDeath + deathBenefitReduced * self.nbrPupDeath

        
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
        surrIf = (self.mathresBA()+self.pbSortDTHS) * self.nbrSurrender
        
        #Rachat des polices réduites
        surrRed = (self.pbAcquAPPUP + self.eppAcquAPPUP) * self.nbrPupSurrender        
        
        
        
# --- AJOUT JO
# Il ne faut pas qu'un rachat soit possible avant 12 mois de la police
        surrIf[self.durationIf() <= 12] = 0
        surrRed[self.durationIf() <= 12] = 0
        
        
        return surrIf + surrRed

#Retourne les échéances (MAT_OUTGO)
    def maturity(self):
        return self.zero()







# =============================================================================
    # --- AJOUT JO 
# =============================================================================


        # --- Calcul RIDERC_OUTGO


 # ici on détermine le capital pour Protection d'avenir en fonction de l'âge
    def capPA(self):
        
        capPA = self.zero()
        capPA[self.age() <= 55]= 25000
        capPA[(self.age() > 55)]= 5000
        capPA[self.age() > 65]= 0
        capPA[self.p['POLPRCPL9'] == 0]=0
        return capPA
    
    
#  calcul de riderINC_PP afin de pouvoir calculé riderCostPP
    def riderIncPP3(self):
        
        riderPP = self.premiumCompl() / self.frac()
    
        return riderPP


# recalcul du taux DC accident pour : (je cite) tenir en compte la sinistralité de la garantie décès de l'epargne en fonction du qx - 26.01.2015

    def dcAccidentAdjusted(self):
        tx1 = self.p['POLPRCPL3'].to_numpy()[:,np.newaxis,np.newaxis] * self.dcAccident()
        tx2 = self.p['POLPRCPL4'].to_numpy()[:,np.newaxis,np.newaxis] * self.exo()
        tx3 = self.p['POLPRCPL9'].to_numpy()[:,np.newaxis,np.newaxis] * self.dcAccident()

        taux = (tx1 + tx2 + tx3) 
        
        result = np.divide(taux, self.premiumCompl(), out=np.zeros_like(taux), where=self.premiumCompl()!=0)
        
        return result
        
        
# prime complémentaire encourue
    
    def riderCostPP(self):
        
    # Age limite pour les complémentaires
        self.agelimite=((self.age()-1)<=self.ageLimite)
        riderC =  self.riderIncPP3() * self.isPremPay() * self.dcAccidentAdjusted() 

        return riderC
    

# benefice en cas de sinistre complémentaire (RIDERC_OUTGO)
    def claimCompl(self):
        
        riderCoutgo = self.riderCostPP() * self.nbrPolIfSM + self.nbrDeath * self.capPA()
        
        return riderCoutgo





        
        # --- MATURITY OUTGO
        
    
# Calcul des sorties dûes aux maturité des polices (MAT_OUTGO)
    def maturity(self):
      
        matBenPP = self.epargnAcquPP + self.pbAcquPP + self.pbSortMatsPP
        noMats = self.nbrNewMat
        pupMatbPP =  self.epAcquAVPUP + self.pbAcquAPPUP
        noPupMat = self.nbrPupMat
 
        matOutgo = self.zero()
      
        for i in range(1,self.shape[1]):
          
            matOutgo[:,i,:] = matBenPP[:,i-1,:] * noMats[:,i,:] + pupMatbPP[:,i-1,:] * noPupMat[:,i,:]
         
#Définition des variables récursives (informatif)
        self.matBenPP = matBenPP
        self.noMats = noMats
        self.pupMatbPP = pupMatbPP
        self.noPupMat = noPupMat
      
        # return matBenIF + matBenPPUPif
        return matOutgo
  







        # --- Calcul pour DeathClaim



# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):

        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        

        mask = calendarMonth ==1
        
        return mask*1



# Taux de participation aux benefices (TX_PB_PC)
    def txPbPC(self):
        
        pbRate = self.pbRate()
        txInt = (self.txInt()**12) - 1
        txPbPC = pbRate - txInt
        return np.round(np.maximum(txPbPC, 0)*100,4)
    
    
    
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
        
        increment = np.cumsum(self.one(), axis = 1)-1

        mask = moisRestant >= increment
        
        return mask


 





    
# =============================================================================
# --- CALCUL DES EXPENSES
# =============================================================================
    
    
    #Retourne le coût par police pour les polices avec réduction possible (RENEXP_XRSE)
    # OK
    def unitExpense(self):
        
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        
        coutParPolice=self.fraisGestion()

        cost=coutParPolice*inflation*(self.nbrPolIfSM + self.nbrPupIfSM)
        
        return cost

    
    
    # Calcul des provisions mathématiques en cours
    # OK
    def provMathIf(self):
        
        provMathIf = self.mathresBA() * self.nbrPolIf + (self.eppAcquAPPUP + self.pbAcquAPPUP) * self.nbrPupsIf
    
        return provMathIf
    
    
    
    
    # calcul des provisions techniques en cours, inforce
    # OK
    def provTechIf(self):
        
        provTechPP = self.provTechPP()
        
        pupMathRes = self.eppAcquAPPUP + self.pbAcquAPPUP
        
        provTechIf = provTechPP * self.nbrPolIf + self.nbrPupsIf * pupMathRes
    
        return provTechIf
    
    
    
    def provTechPP(self):
        
        prov = self.mathresBA() - self.riskEnCours()
    
        return prov
    
    
    
    def provTechPUP(self):
        
        prov = self.eppAcquAPPUP + self.pbAcquAPPUP
    
        return prov
    
    
# diminution de la provision non zilmérisée à la maturité du contrat 
# OK
    def tresRldMat(self):
        
        provTechPP = self.provTechPP()
        provTechPUP = self.provTechPUP()
        noMat = self.nbrNewMat
        noPupMat = self.nbrPupMat
        tresRldMat = self.zero()
        
        for i in range(1,self.shape[1]):
            tresRldMat[:,i,:] = provTechPP[:,i-1,:] * noMat[:,i,:] + provTechPUP[:,i-1,:] * noPupMat[:,i,:]
            
        return tresRldMat
    



# reserve par police réduite
    def pupMathRes(self):
        
        mathRes = self.eppAcquAPPUP + self.pbAcquAPPUP
        return mathRes



    
    def pbIncorpIF(self):
        
        pb = self.pbIncorPP * self.nbrPolIfSM + self.pbIncorPUP * self.nbrPupIfSM
    
        return pb
    
    
    
    #  calcul des provisions techniques ajustée (PROV_TECH_AJ)
    # OK
    def provTechAj(self):
        
        provTechAj = self.zero()
        provTechIf = self.provTechIf()
        primeInvest = self.premiumInvested() * self.nbrPolIfSM
        riderCoutgo = self.claimCompl()

        tresRldMat = self.tresRldMat()
        
        
        pbIncorpIf = self.pbIncorpIF()
        
        for i in range(1,self.shape[1]):
        
            provTechAj[:,i,:] = provTechIf[:,i-1,:] + pbIncorpIf[:,i,:] + primeInvest[:,i,:] - riderCoutgo[:,i,:] - tresRldMat[:,i,:]
        
        return provTechAj
    
    
# calcul des intêret techniques crédités (INT_CRED_T)
# OK
    def intCredT(self):
        
        return (self.txInt()-1) * self.provTechAj()
    
# Dotation PB
# OK
    def dotationPB(self):
        
        pb = self.pbCalcPP * self.nbrPolIf + self.pbCalcPUP * self.nbrPupsIf
        return pb
    
    
# Coût de la PB sur sortie
#OK
    def pbSortie(self):

        nbrNewMat = self.nbrNewMat
        pbInforce = self.zero()
        pbSortMatsPP = self.pbSortMatsPP
        pbSortMatsPUP = self.pbSortMatsPUP

        for i in range(1,self.shape[1]):
            pbInforce[:,i,:] =  pbSortMatsPP[:,i-1,:] * nbrNewMat[:,i,:] 
        return pbInforce
    
    
    
# Reprise pour incorporation de la PB
    def reprisePB(self):
        
        dotationPB = self.dotationPB()
        fondPB = self.zero()
        reprisePB = self.zero()
 
        for i in range(1,self.shape[1]):
            
            reprisePB[:,i,:] = fondPB[:,i-1,:]
            
            fondPB[:,i,:] =  fondPB[:,i-1,:] + dotationPB[:,i,:] - reprisePB[:,i,:]
  
        return reprisePB
    
# meme Méthode car j'ai besoin de fondPB (à changer) 
    def fondPB(self):
        
        dotationPB = self.dotationPB()
        fondPB = self.zero()
        reprisePB = self.zero()
 
        for i in range(1,self.shape[1]):
            
            reprisePB[:,i,:] = fondPB[:,i-1,:]
            
            fondPB[:,i,:] =  fondPB[:,i-1,:] + dotationPB[:,i,:] - reprisePB[:,i,:]
  
        return fondPB
    
    
    

# Reprise sur fond de PB suite à une maturité
    def repPbMats(self):
        
        nbrPupMat= self.nbrPupMat
        nbrNewMat = self.nbrNewMat
        pb = self.zero()
        pbSortMatsPP = self.pbSortMatsPP
        pbSortMatsPUP = self.pbSortMatsPUP
        matRate = self.zero()

        for i in range(1,self.shape[1]):
            pb[:,i,:] =  pbSortMatsPP[:,i-1,:] * nbrNewMat[:,i,:] + pbSortMatsPUP[:,i-1,:] * nbrPupMat[:,i,:]
            
        # Met un 1 lors de la maturité de la police, autrement 0
        matRate[self.polTermM()+1 ==self.durationIf()]=1 
        pb = matRate * pb
        
        return pb
    
    
    
    
# Arrondi des tables ACTU.FAC afin d'obtenir mUfii
    def mUfii(self):
        
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        
        rate = (1+rate)**(1/12) - 1
        return rate
    
    
    
    
# Resultat financier du mois
    def resFinMois(self):
        
        pass
    
    
    
    
#  Calcul des réserve mathématiques adjustées
    def reserveForExp(self):
        
        # déclaration des nouvelles variables
        resReldMat = self.zero()
        totExp = self.zero()
        rfinAnn = self.zero()
        oTaxblInc = self.zero()
        adjMathRes2 = self.zero()
        resFinMois = self.zero()
        provMathAj = self.zero()
        
        # Nombre polices
        nbrPolIf = self.nbrPolIf
        nbrPupsIf = self.nbrPupsIf
        noMat = self.nbrNewMat
        nbrPupMat = self.nbrPupMat
        
        # fonction existantes
        fMathResIF = self.provMathIf() + self.fondPB()
        provMathIf = self.provMathIf()
        riderCoutgo = self.claimCompl()
        pbIncorpIF = self.pbIncorpIF()
        premInc = self.totalPremium()
        pupMathRes = self.pupMathRes()
        fondPB = self.fondPB()
        mUfii = self.mUfii()
        repPbMats = self.repPbMats()
        premInvest = self.premiumInvested() * self.nbrPolIfSM
        unitExp = self.unitExpense()
        reprisePB = self.reprisePB()
        dotationPB = self.dotationPB()
        pbSortie = self.pbSortie()
        totIntCred = self.intCredT()
        provTechAj = self.provTechAj()   
        txReserve = self.fraisGestionPlacement()
        mathresPP = self.mathresBA()  
        totComm = self.commissions()
        monthPb = self.one() - self.allocMonths()
        isActive = self.isActive()
    
        # calcul des exceptions
        # provMathAj[:,0,:] = premInc[:,0,:] - totExp[:,0,:] - riderCoutgo[:,0,:]
    
        # # condition qui met des 1 à polterm + 1
        # cond = self.durationIf() == self.polTermM()+1
        
        for i in range(1,self.shape[1]):
            
            
            resReldMatTEMP = (fondPB[:,i-1,:] + rfinAnn[:,i-1,:])
            
            resReldMat[:,i,:] = np.divide(resReldMatTEMP, (nbrPolIf[:,i-1,:] + nbrPupsIf[:,i-1,:]), out=np.zeros_like(resReldMatTEMP), where=(nbrPolIf[:,i-1,:] + nbrPupsIf[:,i-1,:])!=0)\
                * (noMat[:,i,:] + nbrPupMat[:,i,:]) + mathresPP[:,i-1,:] * noMat[:,i,:] + pupMathRes[:,i-1,:] * nbrPupMat[:,i,:]
            
            
            
       
            # resReldMat[:,i,:] = mathresPP[:,i-1,:] * noMat[:,i,:] + pupMathRes[:,i-1,:] * nbrPupMat[:,i,:] + (fondPB[:,i-1,:] + rfinAnn[:,i-1,:]) / (nbrPolIf[:,i-1,:] + nbrPupsIf[:,i-1,:])*(noMat[:,i,:] + nbrPupMat[:,i,:])
            

        
            adjMathRes2[:,i,:] = fMathResIF[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:] - resReldMat[:,i,:] - repPbMats[:,i,:]
        
            totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
            
            
            provMathAj[:,i,:] = (provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - (totExp[:,i,:] + totComm[:,i,:]) - resReldMat[:,i,:]) * isActive[:,i,:]
        
            oTaxblInc[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            
            
            resFinMois[:,i,:] = oTaxblInc[:,i,:] + reprisePB[:,i,:] - totIntCred[:,i,:] - pbIncorpIF[:,i,:] - dotationPB[:,i,:] - pbSortie[:,i,:]
            
            rfinAnn[:,i,:] = (rfinAnn[:,i-1,:] + resFinMois[:,i,:]) * monthPb[:,i,:] * isActive[:,i,:]
            
            
            
    
            
   #Définition des variables récursives
        # Résultat financier en fin de mois non constaté
        self.resFinMois = resFinMois
        # Résultat de l'année en cours non constaté
        self.rfinAnn=rfinAnn
        # Reserves mathématiques ajustées pour calculer les expenses
        self.adjMathRes2 = adjMathRes2
        # Office taxable Income
        self.oTaxblInc = oTaxblInc
        # Provisions mathématiques ajustées
        self.provMathAj = provMathAj

        self.resReldMat = resReldMat
        
        self.premInvest = premInvest
        
        self.fMathResIF = fMathResIF
  
        
        # total expenses 
        self.totExp = totExp
        

        return

    def reserveExpense(self):
        
        reserveExpense = self.adjMathRes2 
        return reserveExpense


    def totalExpense(self):
        total = self.totExp
        return total
    
    
    

# =============================================================================
# DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES
# =============================================================================


def tester(self):
    return self

pol = EP()

# a = pol.matu()


#pol=EP(run=[4,5])
# pol.ids([1731601, 1732501])
pol.ids([1764401])
# pol.ids([493202, 524401])
# pol.ids([515503,1736301,1900401,2168101,2396001,2500001,2500101,2466301])

# 
# pol.mod([33])

# a = pol.BEL()[:,:409,0]
fff = pol.provMathAj



# riderPP = pol.riderCostPP()

#pol.modHead([9],2)
# aa = pol.p
# a=pol.nbrPolIf
# fff = pol.reprisePB()
#b=pol.nbrPolIfSM
#c=pol.nbrMaturities
# d=pol.nbrDeath
#e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.premiumPure()
# h=pol.deathClaim()
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

pol.p.to_excel('check portefeuille.xlsx')
        


print("Class EP--- %s sec" %'%.2f'%  (time.time() - start_time))

monCas=fff
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
# a = pol.mUfii
# z=pd.DataFrame(a[:,:,0])
# z.to_excel('test mUfii.xlsx')
