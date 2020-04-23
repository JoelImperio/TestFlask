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
        
        #Calcul du risque en cours
        riderIncPP=self.purePremium()*self.isPremPay()*agelimite
        riderIncPP2=self.purePremium()*agelimite
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
        riderCostOutgo=self.premiumPrincipal()*self.dcAccident()*self.isPremPay()*agelimite
        

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

        #L'age limite est erroné, il faudra supprimer cette condition  
        agelimite=(self.age()<=65)
        
        claimRate=self.dcAccident()

        
        premiumPrincipal=self.premiumPrincipal()
        

        premiumPrincipal=premiumPrincipal*agelimite
        
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

#L'age limite est erroné, il faudra supprimer cette condition  
        agelimite=(self.age()-1<=75)
        
           
        annualPrem = (self.p['POLPRVIEHT'] + self.p['POLPRCPL2']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()   
 
        
        #Calcul du risque en cours
        riderIncPP=annualPrem*agelimite*self.isPremPay()
        riderIncPP2=annualPrem*agelimite
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

        #Primes pure encaissées
        annPremPP=(self.p['POLPRVIEHT']+ self.p['POLPRCPL2']).to_numpy()[:,np.newaxis,np.newaxis]
        CaFracPC=self.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        CaPremPC=self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        prInventPP=(annPremPP*(1-CaPremPC))/CaFracPC
        prPurePP=prInventPP
        ppEncPP=(prPurePP/self.frac())*self.isPremPay()
        pPureEnc=ppEncPP*self.nbrPolIfSM
       
        #Sortie pour les claim principaux
        riderCostOutgo=annualPrem*self.hospi()*self.isPremPay()*agelimite
        
        reserve=mathResIfcorr+pPureEnc-riderCostOutgo
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

class PR(Portfolio):
    mods=[25,26]
    ageLimite = 65


    
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
        prem=self.p['POLPRVIEHT']
        return prem.to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
    
#Retourne les primes conditionnés au nombre de polices en vigueur    
    def premiumPrincipal(self):
        return self.purePremium()*self.nbrPolIfSM


#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):

  # Age limite pour hospitalis
        agelimite=((self.age()-1)<=self.ageLimite)*self.one()
           
        annualPrem = (self.p['POLPRVIEHT']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()   
        riderC =  annualPrem * self.isPremPay() *self.dcAccident() * self.nbrPolIfSM
        
        #Calcul du risque en cours
        riderIncPP=annualPrem*agelimite*self.isPremPay()
        riderIncPP2=annualPrem*agelimite
        
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
        agelimite=((self.age()-1)<=self.ageLimite)
        claimRate=self.dcAccident()
        premiumPrincipal=self.premiumPrincipal()
        premiumPrincipal=premiumPrincipal*agelimite
        claim=claimRate*premiumPrincipal*self.isPremPay()
        
        return claim


#Retourne le total des claim pour la garantie principale    
    def claimPrincipal(self):
        return self.deathClaim()

#Retourne le total des claim pour les garanties complémentaires
    def claimCompl(self):
        return self.accidentalDeathClaim() 



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



#Sauvegarde des variables de  PB pour actives et réduites
        
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
        # Pb donnée par police en cas de maturité
        self.pbSortMatsPP = pbSortMatsPP
        # pb donnée par police en cas de maturité d'une police réduite
        self.pbSortMatsPUP = pbSortMatsPUP     
        # pb donnée par police en cas de décès
        self.pbCalcPPdths = pbCalcPPdths
        # pb donné par police en cas de décès d'une police réduite
        self.pbCalcPUPdths = pbCalcPUPdths
        
        return


# =============================================================================
    ### CALCUL DES PRIMES
# =============================================================================


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
        

# A rajouté pour corrigé les risque en cours 
        # precPP[:,0,:] = pol.p['PMBREC'].to_numpy()[:,np.newaxis] 

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
              
        return precPP


# =============================================================================
    ### CALCUL DES CLAIMS 
# =============================================================================


#Retourne les claims décès
    def deathClaim(self):

        addSumAssuree = self.p['POLCAPAUT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        mask_55 = (self.age() <= 55)
        mask_55_65 = (self.age() > 55) & (self.age() <= 65)       
        mask_65 = (self.age() > 65)
      
        addSumAssuree[(self.mask([32])) & mask_55]=30000
        addSumAssuree[(self.mask([32])) & mask_55_65]=7500        
        addSumAssuree[(self.mask([32])) & mask_65]=2500       
        

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

#Retourn la réserve mathémathique incluant la PB
    def mathresBA(self):
        return  self.epargnAcquPP + self.pbAcquPP + self.riskEnCours()   

#Retourne les rachats totaux (SURR_OUTGO)
    def surrender(self):
        
        #Rachats des polices active
        surrIf = (self.mathresBA()+self.pbSortDTHS) * self.nbrSurrender
        
        #Rachat des polices réduites
        surrRed = (self.pbAcquAPPUP + self.eppAcquAPPUP) * self.nbrPupSurrender        
        
# Il ne faut pas qu'un rachat soit possible avant 12 mois de la police
        surrIf[self.durationIf() <= 12] = 0
        surrRed[self.durationIf() <= 12] = 0
        
        return surrIf + surrRed


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
    
    
#Retourne les claims des garanties complémentaires (RIDERC_OUTGO)
    def claimCompl(self):
        
        riderCoutgo = self.riderCostPP() * self.nbrPolIfSM + self.nbrDeath * self.capPA()
        
        return riderCoutgo


    
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

        return matOutgo
  



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
    ### CALCUL DES EXPENSES
# =============================================================================

    
#Retourne le coût par police pour les polices avec réduction possible (RENEXP_XRSE)
    def unitExpense(self):
        
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        
        coutParPolice=self.fraisGestion()

        cost=coutParPolice*inflation*(self.nbrPolIfSM + self.nbrPupIfSM)
        
        return cost

    
    
# Calcul des provisions mathématiques en cours
    def provMathIf(self):
        
        provMathIf = self.mathresBA() * self.nbrPolIf + (self.eppAcquAPPUP + self.pbAcquAPPUP) * self.nbrPupsIf
    
        return provMathIf
    
    
    
    
# calcul des provisions techniques en cours, inforce
    def provTechIf(self):
        
        provTechPP = self.provTechPP()
        
        pupMathRes = self.eppAcquAPPUP + self.pbAcquAPPUP
        
        provTechIf = provTechPP * self.nbrPolIf + self.nbrPupsIf * pupMathRes
    
        return provTechIf
    
    
# Provision technique par polices
    def provTechPP(self):
        
        prov = self.mathresBA() - self.riskEnCours()
    
        return prov
    
    
# Provision technique par contrat réduit
    def provTechPUP(self):
        
        prov = self.eppAcquAPPUP + self.pbAcquAPPUP
    
        return prov
    
    
# diminution de la provision non zilmérisée à la maturité du contrat 
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



# PB incorporée in force
    def pbIncorpIF(self):
        
        pb = self.pbIncorPP * self.nbrPolIfSM + self.pbIncorPUP * self.nbrPupIfSM
    
        return pb
    
    
    
#  calcul des provisions techniques ajustée (PROV_TECH_AJ)

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
    def intCredT(self):
        
        return (self.txInt()-1) * self.provTechAj()
    
# Dotation PB
    def dotationPB(self):
        
        pb = self.pbCalcPP * self.nbrPolIf + self.pbCalcPUP * self.nbrPupsIf
        return pb
    
    
# Coût de la PB sur sortie
    def pbSortie(self):

        nbrNewMat = self.nbrNewMat
        pbInforce = self.zero()
        pbSortMatsPP = self.pbSortMatsPP

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
     

# # Reprise sur fond de PB suite à une maturité
#     def repPbMats(self):
        
#         nbrPupMat= self.nbrPupMat
#         nbrNewMat = self.nbrNewMat
#         pb = self.zero()
#         pbSortMatsPP = self.pbSortMatsPP
#         pbSortMatsPUP = self.pbSortMatsPUP
#         matRate = self.zero()

#         for i in range(1,self.shape[1]):
#             pb[:,i,:] =  pbSortMatsPP[:,i-1,:] * nbrNewMat[:,i,:] + pbSortMatsPUP[:,i-1,:] * nbrPupMat[:,i,:]
            
#         # Met un 1 lors de la maturité de la police, autrement 0
#         matRate[self.polTermM()+1 ==self.durationIf()]=1 
#         pb = matRate * pb
        
#         return pb
    
    
# Reprise sur fond de PB suite à une maturité  
    def repPbMats(self):
        return self.zero()
    
    
# Arrondi des tables ACTU.FAC afin d'obtenir mUfii (table rdt est)
    def mUfii(self):
        
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        
        rate = (1+rate)**(1/12) - 1
        return rate
    
    
#  Calcul des réserve mathématiques adjustées afin de calculer les expenses

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
        txReserve = self.fraisGestionPlacement()
        mathresPP = self.mathresBA()  
        totComm = self.totalCommissions()
        monthPb = self.one() - self.allocMonths()
        isActive = self.isActive()
    
        
        for i in range(1,self.shape[1]):
            
            
            resReldMatTEMP = (fondPB[:,i-1,:] + rfinAnn[:,i-1,:])
            
            resReldMat[:,i,:] = np.divide(resReldMatTEMP, (nbrPolIf[:,i-1,:] + nbrPupsIf[:,i-1,:]), out=np.zeros_like(resReldMatTEMP), where=(nbrPolIf[:,i-1,:] + nbrPupsIf[:,i-1,:])!=0)\
                * (noMat[:,i,:] + nbrPupMat[:,i,:]) + mathresPP[:,i-1,:] * noMat[:,i,:] + pupMathRes[:,i-1,:] * nbrPupMat[:,i,:]
            
            adjMathRes2[:,i,:] = fMathResIF[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:] - resReldMat[:,i,:] - repPbMats[:,i,:]
        
            totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
                
            provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + pbIncorpIF[:,i,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - (totExp[:,i,:] + totComm[:,i,:]) - resReldMat[:,i,:]
        
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
        # diminution des reserves à la maturité
        self.resReldMat = resReldMat
        # prime investie
        self.premInvest = premInvest
        # Provisions mathématiqwues
        self.fMathResIF = fMathResIF
        # total expenses 
        self.totExp = totExp
        
        return


    def reserveExpense(self):
        
        reserveExpense = self.adjMathRes2 * self.fraisGestionPlacement()
        return reserveExpense
    
print("Class EP--- %s sec" %'%.2f'%  (time.time() - start_time))   


# =============================================================================
### TEST ET FONCTIONALITES
# =============================================================================


# pol=FU()
# pol=AX()
# pol = HO()
# pol=PR()
# pol = EP()

# o=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()

# bel=np.sum(pol.BEL(), axis=0)
# pgg=pol.PGG()


# monCas=o

# zz=np.sum(monCas, axis=0)
# zzz=np.sum(zz[:,0])
# z=pd.DataFrame(monCas[:,:,0])
# z=z.sum()
# z.to_csv(path+'/zRW/check.csv',header=False)


# pol.p.to_excel(path+'/zRW/check portefeuille.xlsx')




#Visualiser une dimension d'un numpy qui n'apparait pas
#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])


