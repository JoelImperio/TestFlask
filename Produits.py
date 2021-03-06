from Portefeuille import Portfolio
from Parametres import Inputs
import numpy as np
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

start_time = time.time()

##############################################################################################################################
##############################################################################################################################

myInputs=Inputs()

##############################################################################################################################
#Création de la class Funérailles
##############################################################################################################################
class FU(Portfolio):
    mods=[8,9,12]
    complPremium=60

    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
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

    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
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
    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
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


    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
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

# =============================================================================
# Création de la classe des Temporaires
# =============================================================================
class TE(Portfolio):
    mods=[3,4]
    # modHeads = [3],1
    # complPremium=pol.p['POLPRCPL2']
    ageLimiteCPL = 60
    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
    
#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.commutations()
        self.loopTemp()
        self.reserveForExp()
    
# =============================================================================
    # --- A REMONTER
# =============================================================================
    
# repris des mixtes (POUR EXPENSES)
# reserves inforce
    def provMathIf(self):
        return self.mathResPP * self.nbrPolIf
    
# Repris des mixtes (POUR EXPENSES)
# calcul des provisions techniques en cours, inforce
    def provTechIf(self):
        return self.provTechPP * self.nbrPolIf 


# Repris des mixtes (POUR EXPENSES)
# Arrondi des tables ACTU.FAC afin d'obtenir mUfii (table rdt est)
# méthode suivante à supprimer, il n'y a aucune raison d'arrondir le taux d'intêret !!
    def mUfii(self):
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        rate = (1+rate)**(1/12) - 1
        return rate


# A REMONTER (repris des mixtes) pour calcul CLAIM
# retourne la somme assurée avec le bon format
    def sumAss(self): 
        return self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one() 
    
## Fonction reprise de Produit EP et mixtes (Utilisé dans claim et expenses)
# Vecteur de 1 et 0 permettant de savoir si police toujours active ou non
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask
  
# Reprise des mixtes (POUR CLAIM)
# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth ==1
        return mask*1  
  
 # Reprises des mixtes (POUR CLAIM)
 # Arrondi des tables afin d'obtenir taux pb (table rdt est). Le taux PB va également dépendre du taux d'intêret 
    def txPartPB(self):
        rate = (1+self.pbRate())**12 - 1
        rate = (1+rate)**(1/12) - 1

        # ligne à supprimer pour corriger !! il ne faut pas arrondir ce taux
        rate = np.round(rate, decimals = 6)
        
        txInt = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()/100
        return np.maximum(0, rate - txInt) 
  
 # reprise des mixtes (POUR CLAIM) 
 # Met un vecteur de 1 et 0 (1 si la police possède moins de 12 mois)
    def pmFirstYear(self):
        vec = self.one() * 12
        mask = self.durationIf() <= 12
        vec[mask] = self.durationIf()[mask]
        return vec 
     
# Reprise des Mixtes (POUR CLAIM)
# Valeur actualisé SA (Net single premium value) AExn * capital
    def valSaPP(self):
        # mask ici car au moment de l'échéance de la police, le net Single premium = 0 et non Capital
        mask = self.polTermM() > self.durationIf() 
        valSaPP = self.zero()
        valSaPP[mask] = self.AExn[mask] * self.sumAss()[mask]
        return valSaPP
    
    
# Reprise des mixtes sans le mask pour mod6 et 7 (POUR CLAIM)
# Calcul de la valeur actualisée des premiums
    def valNetPrem(self):
        return self.purePremium() * self.axn 
    


# loop pour temporaire
    def loopTemp(self):

#Variables des actifs  
# Condition me permettant de supprimer les polices qui ont un age à 999 (mis volontairement dans le preprocessing)
        nbrPolIf = self.age() < 999
        nbrPolIf = nbrPolIf * self.one()
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
        lapseTiming=1
        polTermM=self.polTermM()   
        
# Lapse timing = 1, donc on ne prend pas en compte les lapses pour le calcul des death pour ces modalité. A  modifier ?
        lapseD=(1-lapseTiming) * self.lapse()
        lapse = self.lapse()          
        qxy = self.qxExpMens() 
        qx = self.qxExp()
        
# Modification les temporaires 2 tetes sont en fait calculée en fonction de l'assuré 1
        mask = (self.p['POLNBTETE']==2).astype(bool)
        qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
        qxy[mask] = 1-(1-qxy[mask])**(1/12)
        qxyD = lapseTiming * qxy

# Variable actuarielle
        AExn = self.AExn
        axn = self.axn

# Définition du vecteur des maturités (bool)        
        matRate[polTermM+1 ==self.durationIf()]=1 
        
# Déclaration des variables pour le calcul des PM        
        # Variable existante
        zill = self.zero()
        precPP = self.precPP()
        valSaPP = self.valSaPP()
        valNetPP = self.valNetPrem()
        prInventPP = self.prInventaire()
        alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
        valSumAss = self.sumAss() * self.AExn
        provGestPP = self.provGestPP()
        pmFirstYear = self.pmFirstYear()    
        allocMonths = self.allocMonths()
        txPartPB = self.txPartPB()
        duration = self.durationIf()

        # # Nouvelles variables
        valAccrbPP = self.zero()
        pbIncorPP = self.zero()
        pbAcquPP = self.zero()
        pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pbCalcPP = self.zero()
        isActive = self.isActive()
        mathResPP = self.zero()  
        provTechPP = self.zero()
        pmZillCum = self.zero()
        pmZillPP = self.zero()
        pmPourPB = self.zero()
        zill1 = self.zero()
        zill2 = self.zero()
        
        # # Calcul des PM au temps 0 

        mathResPP[:,0,:] = np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] - valNetPP[:,0,:] + precPP[:,0,:] - zill[:,0,:], 0 )

        provTechPP[:,0,:] = mathResPP[:,0,:] - provGestPP[:,0,:] - precPP[:,0,:] + zill[:,0,:]
        
        for i in range(1,self.shape[1]):

#Définition des variables des actifs            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:] - nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseD[:,i,:]))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxyD[:,i,:]))
            
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:] - nbrMaturities[:,i,:]

#Définition des variables des réduites
            nbrPupMaturities[:,i,:]=nbrPupsIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPupIfSM[:,i,:]=nbrPupsIf[:,i-1,:] - nbrPupMaturities[:,i,:]
            
            nbrPupDeath[:,i,:]=nbrPupIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseTiming*lapse[:,i,:]))
            
            nbrPupSurrender[:,i,:]=nbrPupIfSM[:,i,:]*lapse[:,i,:]*(1-(lapseTiming*qxy[:,i,:]))
            
            nbrPupsIf[:,i,:]=nbrPupsIf[:,i-1,:]-nbrPupDeath[:,i,:]-nbrPupSurrender[:,i,:] - nbrPupMaturities[:,i,:] + nbrNewRed[:,i,:]

# Variable permettant le calcul des reserves et pb

            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

# Cette valeur est à 0 pour toutes les modalité 3 et 4
            valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] * 0
            
            # Différence par rapport au mixtes
            zill1[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:])
            zill2[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], 0.8 * (valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:]))
            
            zill[:,i,:] = np.where(duration[:,i,:] <= 24, zill1[:,i,:], zill2[:,i,:])
            
            mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )
            
            provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]


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
        
        # Provisions technique par police 
        self.provTechPP = provTechPP
        # Reserves mathématiques par polices       
        self.mathResPP = mathResPP
        # # Valeur actualisée de la PB 
        self.valAccrbPP = valAccrbPP
        # # Zillmérisation 
        self.zill = zill


# Fonction présent dans l'update permettant de chargé une fois tous les symboles de commutation
    def commutations(self):
        
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Nxt = self.actu('Nx', 't')
        # Nxp = self.actu('Nx', 'p')
        NxDec = self.actu('Nx', 't+1')
        
        Dx = self.actu('Dx', 'x')
        Dxn = self.actu('Dx', 'n')
        Dxt = self.actu('Dx', 't')
        # Dxp = self.actu('Dx', 'p')
        DxDec = self.actu('Dx', 't+1')
        
        Mx = self.actu('Mx', 'x')
        Mxn = self.actu('Mx', 'n')
        Mxt = self.actu('Mx', 't')
        # Mxp = self.actu('Mx', 'p')
        MxDec = self.actu('Mx', 't+1')
  
# AExn
        AExn = self.zero()
        AExn[Dxt>0] = AExn[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] ) / Dxt[Dxt>0]
        
        AExn = np.roll(AExn, -1, axis = 1)
        
        AExnDec = self.zero()
        AExnDec[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0]) / DxDec[DxDec>0]
        AExnDec = np.roll(AExnDec, -1, axis = 1)
        
        AExn = self.interp(AExn, AExnDec)
  
# äxn annuity endowment insurance
        axn = self.zero()
        axn[Dxt>0] = (Nxt[Dxt>0] - Nxn[Dxt>0]) / Dxt[Dxt>0]
        axn = np.roll(axn, -1, axis = 1)
        
        axnDec = self.zero()
        axnDec[DxDec>0] = (NxDec[DxDec>0] - Nxn[DxDec>0]) / DxDec[DxDec>0]
        axnDec = np.roll(axnDec, -1, axis = 1)
        
        axn = self.interp(axn, axnDec)
        
# Calcul des variable pour des polices à 2 têtes           
        Nx = self.actu('Nx', 'x', nbtetes = 2)
        Nxn = self.actu('Nx', 'n', nbtetes = 2)
        Nxt = self.actu('Nx', 't', nbtetes = 2)
        NxDec = self.actu('Nx', 't+1', nbtetes = 2)
        
        Dx = self.actu('Dx', 'x', nbtetes = 2)
        Dxn = self.actu('Dx', 'n', nbtetes = 2)
        Dxt = self.actu('Dx', 't', nbtetes = 2)
        DxDec = self.actu('Dx', 't+1', nbtetes = 2)
        
        Mx = self.actu('Mx', 'x', nbtetes = 2)
        Mxn = self.actu('Mx', 'n', nbtetes = 2)
        Mxt = self.actu('Mx', 't', nbtetes = 2)
        MxDec = self.actu('Mx', 't+1', nbtetes = 2)
        

# AExn endowment insurance 2 tetes
        AExn2t = self.zero()
        AExn2t[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] ) / Dxt[Dxt>0]
        AExn2t = np.roll(AExn2t, -1, axis = 1)
        
        AExnDec2t = self.zero()
        AExnDec2t[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0])  / DxDec[DxDec>0]
        AExnDec2t = np.roll(AExnDec2t, -1, axis = 1)
        
        AExn2t = self.interp(AExn2t, AExnDec2t)
  
# äxn annuity endowment insurance 2t
        axn2t = self.zero()
        axn2t[Dxt>0] = (Nxt[Dxt>0] - Nxn[Dxt>0]) / Dxt[Dxt>0]
        axn2t = np.roll(axn2t, -1, axis = 1)
        
        axnDec2t = self.zero()
        axnDec2t[DxDec>0] = (NxDec[DxDec>0] - Nxn[DxDec>0]) / DxDec[DxDec>0]
        axnDec2t = np.roll(axnDec2t, -1, axis = 1)
        
        axn2t = self.interp(axn2t, axnDec2t)
        
        
        self.AExn = self.zero()
        self.axn = self.zero()
        

        mask2t = self.p['POLNBTETE'] == 2
        mask1t = self.p['POLNBTETE'] == 1
        
        self.AExn[mask1t] = AExn[mask1t]
        self.AExn[mask2t] = AExn2t[mask2t]
        # self.AExn = AExn
        
        self.axn[mask1t] = axn[mask1t]
        self.axn[mask2t] = axn2t[mask2t]
        # self.axn = axn
    
    

# =============================================================================
    # --- CALCUL DES PREMIUMS
# =============================================================================

# Retourne les primes complémentaires
    def premiumCompl(self):
        maskAge = (self.age() <= self.ageLimiteCPL)
        premium = self.p['POLPRCPL1'] + self.p['POLPRCPL2'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5'] + self.p['POLPRCPL6']\
             + self.p['POLPRCPL8'] + self.p['POLPRCPL9']
        premium = premium[:,np.newaxis, np.newaxis]*self.one()  
        total = self.zero()
        total[maskAge] = premium[maskAge] / self.frac()[maskAge]
        return total
    
# Retourne les primes annuelles
    def premInc(self):
        annualPrem = self.p['POLPRVIEHT'][:,np.newaxis, np.newaxis]*self.one() / self.frac()
        return annualPrem
    
# Retourne les primes totales perçues (Je pense qu'il faudrait remonté celle-ci pour remplacé celle existante)
    def totalPremium(self):        
        return ((self.premInc() * self.indexation()) + self.premiumCompl()) * self.nbrPolIfSM * self.isPremPay()

# calcul de la prime pure
    def purePremium(self):
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Dx = self.actu('Dx', 'x')
        Mx = self.actu('Mx', 'x')
        Mxn = self.actu('Mx', 'n')

        AExn = self.zero()
        AExn = (Mx - Mxn ) / Dx
        
        axn = self.zero()
        axn = (Nx - Nxn ) / Dx
        
# Calcul pour les 2têtes 
        Nx = self.actu('Nx', 'x', nbtetes = 2)
        Nxn = self.actu('Nx', 'n', nbtetes = 2)
        Dx = self.actu('Dx', 'x', nbtetes = 2)
        Mx = self.actu('Mx', 'x', nbtetes = 2)
        Mxn = self.actu('Mx', 'n', nbtetes = 2)
        
        AExn2t = self.zero()
        AExn2t = (Mx - Mxn ) / Dx

        axn2t = self.zero()
        axn2t = (Nx - Nxn ) / Dx
        
        mask1t = self.p['POLNBTETE'] == 1
        mask2t = self.p['POLNBTETE'] == 2
        
        AExn[mask2t] = AExn2t[mask2t] 
        axn[mask2t] = axn2t[mask2t]
         
        return (AExn / axn)  * self.sumAss()

# Calcul de la valeur actualisée des primes
    def aduePolVal(self):
        Nx = self.actu('Nx', 'x')
        Nxp = self.actu('Nx', 'p')
        Dx = self.actu('Dx', 'x')
        return (Nx - Nxp ) / Dx

# Valeur actualisée des primes au temps 0 
    def valNetPfac(self):
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Dx = self.actu('Dx', 'x')
        return (Nx - Nxn) / Dx

# Calcul de la prime d'inventaire
    def prInventaire(self):
        return self.purePremium() + self.p['fraisGestDureePoliceSA'][:,np.newaxis, np.newaxis] \
            * self.sumAss() * (self.aduePolVal() / self.valNetPfac()) + self.p['fraisGestDureePrimesSA'][:,np.newaxis, np.newaxis] * self.sumAss()
        
   
# =============================================================================
    # --- CALCUL DES CLAIMS
# =============================================================================


# Il n'y a pas de condition sur l'age de l'assuré ici (A MODIFIER ?)
# determine le taux de sinistralité pour les complémentaires
    def riderCRate(self):
        
        IAD = self.p['POLPRCPL1'][:,np.newaxis, np.newaxis] * self.ipt()
        dblAcc = self.p['POLPRCPL2'][:,np.newaxis, np.newaxis] * self.dcAccident()
        trplAcc = self.p['POLPRCPL3'][:,np.newaxis, np.newaxis] * self.dcAccident()
        exo = self.p['POLPRCPL4'][:,np.newaxis, np.newaxis] * self.exo()
        exoRente = self.p['POLPRCPL5'][:,np.newaxis, np.newaxis] * self.itt()
        hospi = self.p['POLPRCPL6'][:,np.newaxis, np.newaxis] * self.hospi()
        acc = self.p['POLPRCPL9'][:,np.newaxis, np.newaxis] * self.dcAccident()
        
        mask = (self.premiumCompl() > 0)
        total = self.zero()
        total[mask] = (IAD[mask] + dblAcc[mask] + trplAcc[mask] + exo[mask] + exoRente[mask] + hospi[mask] + acc[mask]) / (self.premiumCompl()[mask] * self.frac()[mask])
        return total

# Charges des complémentaires par polices
    def riderCost(self):
        return self.premiumCompl() * self.riderCRate() * self.isPremPay()
            

# Claim complémentaires
    def claimCompl(self):
        return self.riderCost() * self.nbrPolIfSM


# Calcul de la provision de gestion
    def provGestPP(self):
        return self.zero()

    
# Calcul claim prrincipale
    def claimPrincipal(self):
        return self.sumAss() * self.nbrDeath
    
    

# =============================================================================
    # --- CALCUL DES EXPENSES
# =============================================================================

#Retourne le risque en cours
    def precPP(self):
        frek=self.frac()
        premCompl =  self.premiumCompl()
        
        #Calcul du risque en cours
        riderIncPP=premCompl*self.isPremPay()
        riderIncPP2=premCompl   
        precPP = self.zero()
        
# A rajouté pour corrigé les risque en cours 
        # precPP[:,0,:] = self.p['PMBREC'].to_numpy()[:,np.newaxis] 

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
              
        return precPP * self.isActive()


#  calcul des provisions techniques ajustée (PROV_TECH_AJ)
    def provTechAj(self):
        provTechAj = self.zero()
        provTechIf = self.provTechIf()
        primeInvest = self.purePremium() * self.nbrPolIfSM * self.isPremPay() / self.frac()
        riderCoutgo = self.claimCompl() 
        
        for i in range(1,self.shape[1]):
            provTechAj[:,i,:] = provTechIf[:,i-1,:]  + primeInvest[:,i,:] - riderCoutgo[:,i,:] 
        return provTechAj * self.isActive()


  # calcul des intêret techniques crédités (INT_CRED_T) 
    def totIntCred(self):    
        intCredT = (self.txInt()-1) * self.provTechAj()
        intCredT[:,0,:] = 0
        return intCredT


# # loop pour calculer les reserves pour expense ADJ_MATHRES2
    def reserveForExp(self):
        
          # déclaration des nouvelles variables
        resReldMat = self.zero()
        totExp = self.zero()
        rfinAnn = self.zero()
        oTaxblInc = self.zero()
        adjMathRes2 = self.zero()
        resFinMois = self.zero()
        provMathAj = self.zero()
        reprisePB = self.zero()
        
          # Nombre polices
        nbrPolIf = self.nbrPolIf
        noMat = self.nbrNewMat
         
          # fonction existantes
        fMathResIF = self.provMathIf() 
        provMathIf = self.provMathIf()
        riderCoutgo = self.claimCompl()
        premInc = self.totalPremium()
        mUfii = self.mUfii()
        premInvest = self.purePremium() * self.nbrPolIfSM * self.isPremPay() / self.frac()
        unitExp = self.unitExpense()
        totIntCred = self.totIntCred() 
        txReserve = self.fraisGestionPlacement()
        mathresPP = self.mathResPP  
        totComm = self.totalCommissions()
        monthPb = self.one() - self.allocMonths()
        isActive = self.isActive()
          
        for i in range(1,self.shape[1]):
        
         
        
               resReldMat[:,i,:] = np.divide(rfinAnn[:,i-1,:], (nbrPolIf[:,i-1,:]), out=np.zeros_like(rfinAnn[:,i-1,:]), where=(nbrPolIf[:,i-1,:])!=0)\
               * noMat[:,i,:] + mathresPP[:,i-1,:] * noMat[:,i,:] 
            
               adjMathRes2[:,i,:] = fMathResIF[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:] - resReldMat[:,i,:] # - repPbMats[:,i,:]
            
               totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
            
               provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - (totExp[:,i,:] + totComm[:,i,:]) - resReldMat[:,i,:]
            
               oTaxblInc[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            
               resFinMois[:,i,:] = oTaxblInc[:,i,:] - totIntCred[:,i,:]
            
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
        # Provisions mathématiqwues
        self.fMathResIF = fMathResIF
        # total expenses 
        self.totExp = totExp

# reserve ajusté pour calculer les expenses
    def adjustedReserve(self):
        return self.adjMathRes2

print("Class TE--- %s sec" %'%.2f'%  (time.time() - start_time))


# =============================================================================
#   Création de la classe Vie entière
# =============================================================================
  
class VE(Portfolio):
    mods=[1, 11]

    # LapseTimine à 0.5 pour les VE
    lapseTiming = 0.5
    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
    
    # L'update contient les self retournés des loop  
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopVE()
        self.commutations()
    
    # !! Fonction modifiée des lapse car VE lapsent mensuellement, a effacer pour corriger 
    def isLapse(self):
        lapse = self.zero()
        check1 = (self.frac() * (self.durationIf()+12)/12)
        check2 = np.floor((self.frac()*(self.durationIf()+12)/12))
        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [lapse[:,:,:]==0, lapse[:,:,:]==0]
        myLapse=np.select(condlist, choicelist)
        # Le premier mois il n'y a pas de payement car la prime est payé en début de mois et les date de calcul sont en fin de mois
        myLapse[:,0,:] = 0
        return myLapse
    
    # !! Fonction mondifiée des lapse car VE lapsent mensuellement, a effacer pour corriger 
    # Par contre ne pas oublier le mask99 pour la durée
    def lapse(self):
        
        # masque pour la durée de 99 ans
        mask99 = (self.durationIf() <= 99*12)
        
        h=self.hypoSet(self.LapseNew)
        lapseSensiMoins=h.iloc[56,2]
        lapseSensiPlus=h.iloc[57,2]       
        cl=self.p['ClassPGGinit']
        lapseRates=h.iloc[23:32,1:12]
        lapseRates.columns = lapseRates.iloc[0]
        lapseRates=lapseRates.drop(lapseRates.index[0])
        lapseRates=lapseRates.set_index('Year').transpose()
        lapseRates=lapseRates[cl].transpose().to_numpy()
        lapseRates=lapseRates[:,:,np.newaxis,np.newaxis]

        dur=self.durationIf()
        dur=dur[:,:,0][:,:,np.newaxis]*self.oneAllrun()

        condlist = [dur<=12,dur<=24,dur<=36,dur<=48,dur<=60, 
                    dur<=72,dur<=84,dur<=96,dur<=108, 
                    dur>108]
        choicelist = [lapseRates[:,0,:],lapseRates[:,1,:],lapseRates[:,2,:], 
                      lapseRates[:,3,:],lapseRates[:,4,:],lapseRates[:,5,:], 
                      lapseRates[:,6,:],lapseRates[:,7,:],lapseRates[:,8,:], 
                      lapseRates[:,9,:] ]
        mylapse=np.select(condlist, choicelist)

        mylapse[:,:,[3,4]]=mylapse[:,:,[3,4]]*lapseSensiMoins
        mylapse[:,:,2]=mylapse[:,:,2]*lapseSensiPlus
       
        # Dimensionner pour les runs et le portefeuille en appel    
        mylapse=mylapse[:,:,self.runs]
        
        # Prise en compte du taux fractionnel et de la mise en place avant un paiement
        frac=self.frac()
        
        # Fractionnement à 0 sont remplacer par 1
        frac[frac==0]=12
        
        # Modfication, forçage du fractionnement à 12
        # mylapse=1-(1-mylapse)**(1/frac)
        mylapse=1-(1-mylapse)**(1/12)
        
        mylapse= self.isLapse() * mylapse * mask99
        
        return mylapse
     
    # Loop qui calcule les maturités, inforce annuels et mensuels, nombre de morts, nombre de surrenders.    
    def loopVE(self):
        
        # Masque durée projections
        mask98 = (self.durationIf() <= 98*12+1)
        
        # Vecteur mise à zéro
        nbrPolIf = self.one()
        nbrDeath = self.zero()
        nbrSurrender = self.zero()
        nbrPolIfSM = self.zero()
        matRate = self.zero()
        
        # Déclaration de certains vecteurs
        polTermM = self.polTermM()
        matRate[polTermM + 1==self.durationIf()]=1
        qxy = self.qxyExpMens()
        lapse = self.lapse()
         
        # Début du loop
        for i in range(1,self.shape[1]):
            nbrPolIfSM[:,i,:] = nbrPolIf[:,i-1,:] * mask98[:,i,:]
            nbrDeath[:,i,:] = nbrPolIfSM[:,i,:] * qxy[:,i,:] * (1-(lapse[:,i,:] * (1-self.lapseTiming))) 
            nbrSurrender[:,i,:] = nbrPolIfSM[:,i,:] * lapse[:,i,:] * (1-(qxy[:,i,:] * self.lapseTiming))
            nbrPolIf[:,i,:] = nbrPolIf[:,i-1,:] - nbrDeath[:,i,:] - nbrSurrender[:,i,:]

        #Nombre de polices actives                                 
        self.nbrPolIf = nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM = nbrPolIfSM
        #Nombre de décès
        self.nbrDeath = nbrDeath 
        #Nombre d'annulation de contrat
        self.nbrSurrender = nbrSurrender * mask98

    # Fonction qui sert à déterminer si une police est active ou non par rapport à sa situation, peut-être doublon
    def policeActive(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis] * self.one()
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result =[(1)]
        sinon = 0
        policeActive = np.select(conditions,result,sinon)
        return policeActive
    
    # Fonction qui sert à déterminer à partir de quand les primes ne sont plus payées (POLDURP)
    def payPrimes(self):
        durationIf = self.durationIf()
        payPrimes = self.one()
        moisPaiement = (self.p['POLDURP'].to_numpy() * 12 )[:,np.newaxis,np.newaxis] * self.one()
        conditions = [(durationIf <= moisPaiement)]
        result =[(1)]
        sinon = 0
        payPrimes = np.select(conditions,result,sinon)
        return payPrimes
    
    # Fonction qui sert à retourner les valeurs actuarielles, Ax, ax, etc.
    def commutations(self):
        
        # Création des variables actuarielles utilisées
        Nx = self.actu('Nx', 'x')
        Nxt = self.actu('Nx', 't')
        Nxp = self.actu('Nx', 'p')
        NxtDec = self.actu('Nx', 't+1')
        Dxt = self.actu('Dx', 't')
        DxtDec = self.actu('Dx', 't+1')
        Mx = self.actu('Mx', 'x')
        Mxt = self.actu('Mx', 't')
        MxtDec = self.actu('Mx', 't+1')

        # Calcul de ax
        ax = self.zero()
        ax[Dxt>0] = Nxt[Dxt>0] / Dxt[Dxt>0]
        ax = np.roll(ax, -1, axis = 1)
        axDec = self.zero()
        axDec[DxtDec>0] = NxtDec[DxtDec>0] / DxtDec[DxtDec>0]
        axDec = np.roll(axDec, -1, axis = 1)
        ax = self.interp(ax, axDec)
        
        # Calcul de axp
        axp = self.zero()
        axp[Dxt>0] = (Nxt[Dxt>0] - Nxp[Dxt>0]) / Dxt[Dxt>0]
        axp = np.roll(axp, -1, axis = 1)
        axpDec = self.zero()
        axpDec[DxtDec>0] = (NxtDec[DxtDec>0] - Nxp[DxtDec>0]) / DxtDec[DxtDec>0]
        axpDec = np.roll(axpDec, -1, axis = 1)
        axp = self.interp(axp, axpDec)
        
        # Calcul de Ax
        Ax = self.zero()
        Ax[Dxt>0] = Mxt[Dxt>0] / Dxt[Dxt>0]
        Ax = np.roll(Ax, -1, axis = 1)
        AxDec = self.zero()
        AxDec[DxtDec>0] = MxtDec[DxtDec>0] / DxtDec[DxtDec>0]
        AxDec = np.roll(AxDec, -1, axis = 1)
        Ax = self.interp(Ax, AxDec)
        
        # Calcul de aduePolVal
        aduePolVal = Nx / (Nx - Nxp)
        
        # Calcul de axInitPrimes
        axInitPrimes = (Nx - Nxp) / Mx
        
        # Retour des variables voulues
        self.ax = ax
        self.axp = axp
        self.Ax = Ax
        self.aduePolVal = aduePolVal
        self.axInitPrimes = axInitPrimes
   
# =============================================================================
    ### FONCTIONS A REMONTER
# =============================================================================
 
    # Fonction piquée dans les épargnes
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth == 1
        return mask*1

    # Fonction prise des épargnes qui n'avait pas été remontée  
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask
    
    # Piqué dans les épargnes
    def mUfii(self):
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        rate = (1+rate)**(1/12) - 1
        return rate
      
# =============================================================================
    ### CALCUL DES PRIMES
# =============================================================================

    # !! Retourne les primes totales perçues, fonction modifiée à cause de la complémentaire à déduire, faux
    def totalPremium(self):
        agelimite = (self.age()>85) 
        mask1 = self.p['PMBMOD'].isin([1])
        prTot = self.p['POLPRTOT'][:,np.newaxis,np.newaxis]
        prCompl = self.p['POLPRCPL3'][:,np.newaxis,np.newaxis]
        # !! La prime complémentaire est déduite après 85 ans pour la mod1 mais pas pour la 11; elle ne doit pas être déduite
        premInc = prTot / self.frac()
        premInc[mask1] = (prTot[mask1] - (prCompl[mask1] * agelimite[mask1])) / self.frac()[mask1]
        prem = premInc * self.nbrPolIfSM * self.isPremPay() * self.indexation()
        return prem * self.payPrimes() 
    
    # !! Comportement bizarre en fin de projection répliqué
    def qxyExpMens(self):
        maskotte1 = self.durationIf() > 98*12
        maskotte2 = self.durationIf() <= 99*12
        mask = maskotte1 & maskotte2
        mask121 = (self.age() <= 121)
        qx = self.qxExpMens(ass=1)
        qy = self.qxExpMens(ass=2)
        return (qx + qy - qx * qy) * mask121 + mask
    
    # Frais sur durée due la police
    def fraisGestDureePoliceSA(self):
        return self.p['fraisGestDureePoliceSA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
    
    # Frais sur durée du paiement des primes
    def fraisGestDureePrimesSA(self):
        return self.p['fraisGestDureePrimesSA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
      
    # Primes brutes mensuelles (ne dépend pas de isprempay)  
    def primeTotaleMensuelle(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotale = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        return primeTotale / frac

    # SUM_ASSD_PP - capital de la police
    def insuredSum(self):
        mask99 = (self.durationIf() <= 99*12)
        sumAssdPp = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one() 
        return sumAssdPp * mask99
    
    # VAL_SUM_ASSD - Capital multiplié par les Ax
    def valSumAssd(self): 
        valSumAssd = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one() 
        return valSumAssd * self.Ax

    # PR_PURE_PP - Prime pure calcul éronné pour la mod11
    def purePremium(self):
        purePremium = self.insuredSum() / self.axInitPrimes * self.policeActive() * self.payPrimes()
        
        # !! calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        mask99 = (self.durationIf() <= 99*12)
        insuredSum = self.insuredSum()
        purePremium[(self.mask([11])) & mask99] = insuredSum[(self.mask([11])) & mask99] / 99
        return purePremium
    
    # PR_INVENT_PP prime d'inventaire (prime pure + les frais de gestion sur somme assurée)
    def prInventPP(self):
        purePremium = self.purePremium()
        cgSaPolPc = self.fraisGestDureePoliceSA()
        cgSaPriPc = self.fraisGestDureePrimesSA()
        insuredSum = self.insuredSum()
        policeActive = self.policeActive()
        aduePolVal = self.aduePolVal
        mask99 = (self.durationIf() <= 99*12)
        prInventPp = purePremium + (cgSaPolPc * aduePolVal + cgSaPriPc) * insuredSum * policeActive
        
        # !! Le calcul pour la 1 devrait être commun à la 11 et la 1
        prInventPp[(self.mask([11]))] = purePremium[(self.mask([11]))] + (cgSaPolPc[(self.mask([11]))] + cgSaPriPc[(self.mask([11]))]) * insuredSum[(self.mask([11]))] * policeActive[(self.mask([11]))] * mask99[(self.mask([11]))]
        return prInventPp            
                      
# =============================================================================
    ### CALCUL DES CLAIMS   
# =============================================================================

    # DEATH_BEN_PP - calcul du death benefit
    def deathBenefit(self):
        
        capital = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]    
        frac = 12 / self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        frac = 12 / self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        pbAcq = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]
        durationif = self.durationIf()  
        isPremPay = self.isPremPay()
        
        conditions = [durationif[:,0,:] != 1, durationif[:,0,:] == 1]
        result =[np.ceil(durationif[:,0,:]/frac[:,0,:]), 1]
        isPremPay[:,0,:] = np.select(conditions,result)
        
        premiumsPaid = isPremPay * self.p['POLPRTOT'][:,np.newaxis,np.newaxis] / self.frac()           
        cumulatedPremiums = self.zero()
        cumulatedPremiums = np.cumsum(premiumsPaid, axis=1)      
        
        conditions = [(durationif>12)]
        result = [(0)]
        sinon = 1
        deathBenPP1 = np.select(conditions,result,sinon) * cumulatedPremiums
        
        conditions = [(durationif>12)]
        result = [(1)]
        sinon = 0
        durationif12plus = np.select(conditions,result,sinon)
        
        deathBenPP2 = (capital + pbAcq) * durationif12plus  
        
        return deathBenPP1 + deathBenPP2
    
    # SURRENDER_OUTGO - Claims réductions
    def surrender(self):
        conditions = [(self.durationIf()>36)]
        result =[(self.mathResBa() * self.nbrSurrender)]
        sinon = 0
        surrOutgo = np.select(conditions,result,sinon)
        return surrOutgo
    
    # DEATH_OUTGO - Claims garantie principale
    def claimPrincipal(self):
        return self.deathBenefit() * self.nbrDeath
    
    # RIDERC_OUTGO - Claims complémentaires
    def claimCompl(self):
    
        totalPremium = self.totalPremium()
        cpl3 = (self.p['POLPRCPL3'])[:,np.newaxis,np.newaxis]/self.frac()
        dcAccident = self.dcAccident()    
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        ridercOutgo = self.zero()
        zero = self.zero()
        isPremPay = self.isPremPay()
        nbrPolIfSM = self.nbrPolIfSM
        
        mask_infeqf85 = (self.age() <= 85) & (situation != 4) & (situation != 8) & (situation != 9)
        mask_sup85 = (self.age() > 85) & (situation != 4) & (situation != 8) & (situation != 9)  
        
        ridercOutgo[mask_infeqf85] = cpl3[mask_infeqf85] * dcAccident[mask_infeqf85] * isPremPay[mask_infeqf85] * nbrPolIfSM[mask_infeqf85]
        ridercOutgo[mask_sup85] = zero[mask_sup85] 
        
        # !! Faux, à enlever, il ne faut pas prendre le totalPremium mais la cpl3
        ridercOutgo[(self.mask([11])) & mask_infeqf85] = totalPremium[(self.mask([11])) & mask_infeqf85] * dcAccident[(self.mask([11])) & mask_infeqf85]
        ridercOutgo[(self.mask([11])) & mask_sup85] = zero[(self.mask([11])) & mask_sup85] 

        return ridercOutgo * self.payPrimes()

    # MATH_RES_BA - provision mathématique 
    def mathResBa(self):
        mask11 = self.p['PMBMOD'].isin([11])
        
        # pour la 01 (cas général?):
        mathResBa = np.maximum(self.valSumAssd() + self.valPrecPP() - self.valNetpPP() + self.provGestPP() - self.valZillPP() + self.valAccrbPP(), 0)
        
        # pour la 11:
        mathResBa[mask11] = np.maximum(self.insuredSum()[mask11] + self.valPrecPP()[mask11] - self.valNetpPP()[mask11]  + self.provGestPP()[mask11]   - self.valZillPP()[mask11] + self.valAccrbPP()[mask11], 0)
        
        return mathResBa
    
    # VAL_ZILL_PP - valeur de zillmérisation    
    def valZillPP(self):
        valZillPC = self.p['tauxZill'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        ValZillPP = np.minimum(valZillPC * self.prInventPP() * self.valNetpFac(), self.valSumAssd() - self.valNetpPP() + self.provGestPP())
        ValZillPP[(self.mask([11]))] = np.minimum(valZillPC[(self.mask([11]))] * self.prInventPP()[(self.mask([11]))] * self.valNetpFac()[(self.mask([11]))], self.insuredSum()[(self.mask([11]))] - self.valNetpPP()[(self.mask([11]))] + self.provGestPP()[(self.mask([11]))])
        return ValZillPP
    
    # PROV_GEST_PP - Provision de gestion par police, quelle logique
    def provGestPP(self):
        
        # PMG_SA_PC - traitement des frais pour provGestPP
        pmgSaPc = self.fraisGestDureePrimesSA() * self.valNetpFac() + self.fraisGestDureePoliceSA() * self.valPolFac()
        
        return pmgSaPc * (self.insuredSum() + self.valAccrbPP()) - self.valNetpFac() * (self.prInventPP() - self.purePremium())
    
    # VAL_PREC_PP - risque en cours
    def valPrecPP(self):
        agelimite=(self.age()<=85)
        primecompl = (self.p['POLPRCPL3'])[:,np.newaxis,np.newaxis] / self.frac()
        riderIncPP = self.zero()
        riderIncPP2 = self.zero()
        primeTotaleMensuelle = self.primeTotaleMensuelle()
        isPremPay = self.isPremPay()
        payPrimes = self.payPrimes()
        
        # Calcul du risque en cours
        riderIncPP = primecompl * self.isPremPay() * agelimite * payPrimes
        riderIncPP2 = primecompl * agelimite * payPrimes
        
        # !! Faux, à enlever, il ne faut pas prendre le totalPremium mais la cpl3
        riderIncPP[(self.mask([11]))] = primeTotaleMensuelle[(self.mask([11]))] * isPremPay[(self.mask([11]))] * agelimite[(self.mask([11]))] 
        riderIncPP2[(self.mask([11]))] = primeTotaleMensuelle[(self.mask([11]))] * agelimite[(self.mask([11]))] 

        precPPbis=self.zero()
        frek=self.frac()
        
        for i in range(1,self.shape[1]):
            precPPbis[:,i,:] = precPPbis[:,i-1,:] + riderIncPP[:,i,:] - ((frek[:,i,:] / 12) * riderIncPP2[:,i,:])
        
        return precPPbis * self.isActive() 
    
    # VAL_POL_FAC - annuité qui dépend de la durée du contrat (faux pour sérénité)
    def valPolFac(self):
        valPolFac = self.ax
        # !! calcul erronné pour la modalité 11, à enlever une fois PGG répliquée:
        durationIf = self.durationIf()
        valPolFac[(self.mask([11]))] = (99 - (durationIf[(self.mask([11]))]/12))
        return valPolFac
    
    # VAL_NETP_PP valeur des primes nettes
    def valNetpPP(self):
        return self.purePremium() * self.valNetpFac()
    
    # VAL_NETP_FAC - annuité qui dépend de la durée de paiemnet des primes (ax, axp, faux pour sérénité)
    def valNetpFac(self):
        dureePayPrimes = self.p['POLDURP'][:,np.newaxis,np.newaxis] * self.one()
        maskDureeEq99 = dureePayPrimes == 99 
        masDureeNotEq99 = dureePayPrimes != 99
        
        ax = self.ax
        axp = self.axp
        policeActive = self.policeActive()
        
        valNetpFac = self.zero()
        valNetpFac[maskDureeEq99] = np.maximum(ax[maskDureeEq99] * policeActive[maskDureeEq99],0)
        valNetpFac[masDureeNotEq99] = np.maximum(axp[masDureeNotEq99] * policeActive[masDureeNotEq99],0)
        
        # !! calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        mask99 = (self.durationIf() <= 99*12)
        durationIf = self.durationIf()
        policeActive = self.policeActive()
        valNetpFac[(self.mask([11])) & mask99] = (99 - (durationIf[(self.mask([11])) & mask99]/12))*policeActive[(self.mask([11])) & mask99]

        return valNetpFac
    
    # VAL_ACCRB_PP - valeur de la PB acquise en début de projection               
    def valAccrbPP(self):
        return self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
    
# =============================================================================
    ### CALCUL DES EXPENSES
# =============================================================================

    # F_MATH_RES_IF - prov math actualisée avec les inforce
    def fMathResIf(self):
        fMathResIf = self.mathResBa() * self.nbrPolIf
        return fMathResIf    
   
    def unitExpense(self):
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:] = 0
        coutParPolice=self.fraisGestion()
        cost=coutParPolice*inflation*self.nbrPolIfSM
        return cost

    #  Calcul des réserve mathématiques adjustées
    def reserveForExp(self):
        
        # déclaration des variables utilisées
        totExp = self.zero()
        rfinAnn = self.zero()
        adjMathRes2 = self.zero()
        resFinMois = self.zero()
        provMathAj = self.zero()
        oExp = self.zero()
        oTaxblInc = self.zero()
        totCom = self.totalCommissions()
        fMathResIf = self.fMathResIf()
        riderCoutgo = self.claimCompl()
        premInc = self.totalPremium()
        provMathIf = self.mathResBa() * self.nbrPolIf
        mUfii = self.mUfii()
        monthPb = self.one() - self.allocMonths()
        totIntCred = self.totalIntCred() 
        premInvest = self.purePremium() * self.nbrPolIfSM / self.frac() * self.isPremPay() * self.policeActive()
        unitExp = self.unitExpense() 
        txReserve = self.fraisGestionPlacement()
        
        # calcul des exceptions
        provMathAj[:,0,:] = premInc[:,0,:] - totExp[:,0,:] - riderCoutgo[:,0,:]
        
        # Loop des expense
        for i in range(1,self.shape[1]):
            adjMathRes2[:,i,:] = np.maximum(0, fMathResIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:])
            totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
            oExp[:,i,:] = totExp[:,i,:] + totCom[:,i,:]
            provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - oExp[:,i,:]
            oTaxblInc[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            resFinMois[:,i,:] = oTaxblInc[:,i,:] - totIntCred[:,i,:]
            rfinAnn[:,i,:] = (rfinAnn[:,i-1,:] + resFinMois[:,i,:]) * monthPb[:,i,:] 

   #Définition des variables récursives (celles inutiles pour runner le code sont commentées)
        # Résultat financier en fin de mois non constaté
        # self.resFinMois = resFinMois
        # Résultat de l'année en cours non constaté
        # self.rfinAnn = rfinAnn
        # Reserves mathématiques ajustées pour calculer les expenses
        # self.adjMathRes2 = adjMathRes2
        # Provisions mathématiques ajustées
        # self.provMathAj = provMathAj
        # Total des expenses
        # self.totExp = totExp
        return adjMathRes2

    def reserveExpense(self):
        # reserveExpense = self.adjMathRes2 * self.fraisGestionPlacement()
        # reserveExpense = self.reserveForExp() * self.fraisGestionPlacement()
        return self.reserveForExp() * self.fraisGestionPlacement()
          
    # Total des intérêts crédités
    def totalIntCred(self):
        
        # Intérêts crédités sur zillmérisation
        valZillIf = self.valZillPP() * self.nbrPolIf
        intCredZill = (self.txInt()-1) * -1 * np.roll(valZillIf, 1, axis=1)
        
        # Intérêts techniques crédités
        intCredT = (self.txInt()-1) * self.provTechAj()
        
        # Intérêts crédités sur PMG
        provGestIf = self.provGestPP() * self.nbrPolIf
        intCredPgm = (self.txInt()-1) * np.roll(provGestIf, 1, axis=1)
        
        # totalIntCred = self.intCredT() + self.intCredZill() + self.intCredPgm()
        totalIntCred = intCredT + intCredZill + intCredPgm
        # ? Doivent-ils être à zéro pour la 11? Positifs pour la 1?
        totalIntCred[(self.mask([11]))] = self.zero()[(self.mask([11]))]
        return totalIntCred
      
    # Provision technique ajustée
    def provTechAj(self):
        
        # Prime pure encourue
        ppureEnc = self.nbrPolIfSM * self.purePremium() / self.frac() * self.isPremPay()
        
        # Provision technique par polices
        provTechPP = self.mathResBa() - self.provGestPP() - self.valPrecPP() + self.valZillPP()
        
        # calcul des provisions techniques en cours
        provTechIf = provTechPP * self.nbrPolIf 
        provTechIf = np.roll(provTechIf, 1, axis = 1)
        provTechIf[:,0,:] = 0
        return provTechIf + ppureEnc - self.claimCompl()

print("Class VE--- %s sec" %'%.2f'%  (time.time() - start_time))


##############################################################################################################################
#Création de la class Epargne
############################################################################################################################

class EP(Portfolio):
    mods=[28,29,30,31,32,33,36]
    ageLimite = 75   

    
    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
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
# Création de la class Mixtes
# =============================================================================
class MI(Portfolio):
    mods=[2,10,6,7]


#Products: F1XT_1,F2XT_1,F1XT14,F1XT11
    
    # age limite pour la garantie complémentaire CPL1
    ageLimiteCPL1 = 60
    ageLimiteCPL2 = 65

    def __init__(self,inputs=myInputs,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(inp=inputs,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.commutations()
        self.loopSaving()
        self.reserveForExp()

# =============================================================================
    ### FONCTION A REMONTER
# =============================================================================

# Vient de EP()
# Calcul des expenses venant des reserves (les frais de gestion des placements) (EXPENSES)
    def reserveExpense(self):
        reserveExpense = self.adjMathRes2 * self.fraisGestionPlacement()
        return reserveExpense
    

# Celle-ci vient aussi de produit EP, je pense qu'on peut remplacé celle qui existe dans portefeuille (la différence est qu'ici il y a nbrPupIfSM 
# et celui-ci est à 0 dans les mixtes, funérailles...) A tester si cela ne casse pas les produits déjà existant (EXPENSES)
# Retourne le coût par police pour les polices avec réduction possible (RENEXP_XRSE) 
    def unitExpense(self):
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        coutParPolice=self.fraisGestion()
        cost=coutParPolice*inflation*(self.nbrPolIfSM + self.nbrPupIfSM)
        return cost

## Fonction reprise de Produit EP (CLAIM)
# ici on détermine le capital pour Protection d'avenir en fonction de l'âge
    def capPA(self):
        capPA = self.zero()
        capPA[self.age() <= 55]= 25000
        capPA[self.age() > 55]= 5000
        capPA[self.age() > 65]= 0
        capPA[self.p['POLPRCPL9'] == 0]=0
        return capPA

## Fonction reprise de Produit EP (Utilisé dans claim et expenses)
# Vecteur de 1 et 0 permettant de savoir si police toujours active ou non
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask

## Fonction reprise de Produit EP (EXPENSES)
# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth ==1
        return mask*1
    
# A corriger afin de pouvoir prendre en compte dans le futur les 2ème têtes de manière correcte (remonté quand celle-ci sera juste)
# Fonction présent dans l'update permettant de chargé une fois tous les symboles de commutation
    def commutations(self):
        
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Nxt = self.actu('Nx', 't')
        # Nxp = self.actu('Nx', 'p')
        NxDec = self.actu('Nx', 't+1')
        
        Dx = self.actu('Dx', 'x')
        Dxn = self.actu('Dx', 'n')
        Dxt = self.actu('Dx', 't')
        # Dxp = self.actu('Dx', 'p')
        DxDec = self.actu('Dx', 't+1')
        
        Mx = self.actu('Mx', 'x')
        Mxn = self.actu('Mx', 'n')
        Mxt = self.actu('Mx', 't')
        # Mxp = self.actu('Mx', 'p')
        MxDec = self.actu('Mx', 't+1')
  
# AExn endowment insurance
        AExn = self.zero()
        AExn[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] + Dxn[Dxt>0]) / Dxt[Dxt>0]
        AExn = np.roll(AExn, -1, axis = 1)
        
        AExnDec = self.zero()
        AExnDec[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0] + Dxn[DxDec>0]) / DxDec[DxDec>0]
        AExnDec = np.roll(AExnDec, -1, axis = 1)
        
        AExn = self.interp(AExn, AExnDec)
  
# äxn annuity endowment insurance
        axn = self.zero()
        axn[Dxt>0] = (Nxt[Dxt>0] - Nxn[Dxt>0]) / Dxt[Dxt>0]
        axn = np.roll(axn, -1, axis = 1)
        
        axnDec = self.zero()
        axnDec[DxDec>0] = (NxDec[DxDec>0] - Nxn[DxDec>0]) / DxDec[DxDec>0]
        axnDec = np.roll(axnDec, -1, axis = 1)
        
        axn = self.interp(axn, axnDec)
        
    
# Calcul des variable pour des polices à 2 têtes       
        
        Nx = self.actu('Nx', 'x', nbtetes = 2)
        Nxn = self.actu('Nx', 'n', nbtetes = 2)
        Nxt = self.actu('Nx', 't', nbtetes = 2)
        NxDec = self.actu('Nx', 't+1', nbtetes = 2)
        
        Dx = self.actu('Dx', 'x', nbtetes = 2)
        Dxn = self.actu('Dx', 'n', nbtetes = 2)
        Dxt = self.actu('Dx', 't', nbtetes = 2)
        DxDec = self.actu('Dx', 't+1', nbtetes = 2)
        
        Mx = self.actu('Mx', 'x', nbtetes = 2)
        Mxn = self.actu('Mx', 'n', nbtetes = 2)
        Mxt = self.actu('Mx', 't', nbtetes = 2)
        MxDec = self.actu('Mx', 't+1', nbtetes = 2)
        

# AExn endowment insurance 2 tetes
        AExn2t = self.zero()
        AExn2t[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] + Dxn[Dxt>0]) / Dxt[Dxt>0]
        AExn2t = np.roll(AExn2t, -1, axis = 1)
        
        AExnDec2t = self.zero()
        AExnDec2t[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0] + Dxn[DxDec>0]) / DxDec[DxDec>0]
        AExnDec2t = np.roll(AExnDec2t, -1, axis = 1)
        
        AExn2t = self.interp(AExn2t, AExnDec2t)
  
# äxn annuity endowment insurance 2t
        axn2t = self.zero()
        axn2t[Dxt>0] = (Nxt[Dxt>0] - Nxn[Dxt>0]) / Dxt[Dxt>0]
        axn2t = np.roll(axn2t, -1, axis = 1)
        
        axnDec2t = self.zero()
        axnDec2t[DxDec>0] = (NxDec[DxDec>0] - Nxn[DxDec>0]) / DxDec[DxDec>0]
        axnDec2t = np.roll(axnDec2t, -1, axis = 1)
        
        axn2t = self.interp(axn2t, axnDec2t)
        
        
        self.AExn = self.zero()
        self.axn = self.zero()
        
        mask10 = self.p['PMBMOD'] == 10
        mask2t = self.p['POLNBTETE'] == 2
        mask1t = self.p['POLNBTETE'] == 1
        
        self.AExn[mask1t | mask10] = AExn[mask1t | mask10]
        self.AExn[mask2t & (~mask10)] = AExn2t[mask2t & (~mask10)]
        
        
        self.axn[mask1t | mask10] = axn[mask1t | mask10]
        self.axn[mask2t & (~mask10)] = axn2t[mask2t & (~mask10)]


# Ne plus remonté à partir d'ici
# =============================================================================
# AJUSTEMENT DE VARIABLES
# =============================================================================


#Retourne la probabilité de décès d'expérience (FAUSSE DANS PROPHET POUR LES MODALITES 6 ET 7 CAR LA MORTALITE D'EXPERIENCE EST A 100%) A SUPPRIMER POUR CORRIGER !!
    def qxExp(self,assExp=1):
        
        mortExp = self.dc()
        # On ajuste la mortalité d'expérience pour modalité 6 et 7 (A SUPPRIMER POUR CORRIGER)
        mod = self.p['PMBMOD'].to_numpy()[:,np.newaxis,np.newaxis]  * self.one()
        mask = ((mod == 7) | (mod == 6))
        mortExp[mask] = 1
        myQx=self.qx(ass=assExp)*mortExp
        
        return np.copy(myQx)


#Retourne les taux de rachat selon le fractionnement. Les taux apparaissent uniquement le mois avant un paiement de prime (pas pour les mixtes) A SUPPRIMER POUR CORRIGER !!
    def lapse(self):

        h=self.hypoSet(self.LapseNew)
        
        lapseSensiMoins=h.iloc[56,2]
        lapseSensiPlus=h.iloc[57,2]       
        cl=self.p['ClassPGGinit']
        
        lapseRates=h.iloc[23:32,1:12]
        lapseRates.columns = lapseRates.iloc[0]
        lapseRates=lapseRates.drop(lapseRates.index[0])
        lapseRates=lapseRates.set_index('Year').transpose()
        lapseRates=lapseRates[cl].transpose().to_numpy()
        lapseRates=lapseRates[:,:,np.newaxis,np.newaxis]

        dur=self.durationIf()
        dur=dur[:,:,0][:,:,np.newaxis]*self.oneAllrun()
        

        condlist = [dur<=12,dur<=24,dur<=36,dur<=48,dur<=60, 
                    dur<=72,dur<=84,dur<=96,dur<=108, 
                    dur>108]
        choicelist = [lapseRates[:,0,:],lapseRates[:,1,:],lapseRates[:,2,:], 
                      lapseRates[:,3,:],lapseRates[:,4,:],lapseRates[:,5,:], 
                      lapseRates[:,6,:],lapseRates[:,7,:],lapseRates[:,8,:], 
                      lapseRates[:,9,:] ]
        mylapse=np.select(condlist, choicelist)

        
        mylapse[:,:,[3,4]]=mylapse[:,:,[3,4]]*lapseSensiMoins
        mylapse[:,:,2]=mylapse[:,:,2]*lapseSensiPlus
       
        #Dimensionner pour les runs et le portefeuille en appel    
        mylapse=mylapse[:,:,self.runs]
        
        #Prise en compte du taux fractionnel et de la mise en place avant un paiement
        # frac=self.frac()
        frac=12*self.one()
        
        #Fractionnement à 0 sont remplacer par 1
        frac[frac==0]=12
        mylapse=1-(1-mylapse)**(1/frac)
        # mylapse= self.isLapse()*mylapse
        
        return mylapse


#Cette Loop renvoie l'ensemble des variables récusrives pour les produits épargnes
    def loopSaving(self):

#Variables des actifs  
# Condition me permettant de supprimer les polices qui ont un age à 999 (mis volontairement dans le preprocessing)
        nbrPolIf = self.age() < 999
        nbrPolIf = nbrPolIf * self.one()
        
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
        qxy = self.qxExpMens() 
        qx = self.qxExp()
        
    # Modification les mixtes 2 tetes sont en fait calculée en fonction de l'assuré 1 (Ce qui est faux) (A MODIFIER) ?
        mask = (((self.p['PMBMOD']==2) & (self.p['POLNBTETE']==2))).astype(bool)
        qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
        qxy[mask] = 1-(1-qxy[mask])**(1/12)
        qxyD = lapseTiming * qxy

        # Variable actuarielle
        AExn = self.AExn

        #Définition du vecteur des maturités (bool)        
        matRate[polTermM+1 ==self.durationIf()]=1 
        
# Déclaration des variables pour le calcul des PM        
        # Variable existante
        zill = self.zero()
        precPP = self.precPP()
        valSaPP = self.valSaPP()
        valNetPP = self.valNetPrem()
        prInventPP = self.prInventaire()
        alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
        axn = self.axn
        valSumAss = self.sumAss() * self.AExn
        provGestPP = self.provGestPP()
        pmFirstYear = self.pmFirstYear()    
        allocMonths = self.allocMonths()
        txPartPB = self.txPartPB()

        
        nbtete = self.p['POLNBTETE'][:,np.newaxis, np.newaxis]*self.one() 
        
        
        # Nouvelles variables
        valAccrbPP = self.zero()
        pbIncorPP = self.zero()
        pbAcquPP = self.zero()
        pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pbCalcPP = self.zero()
        isActive = self.isActive()
        mathResPP = self.zero()  
        provTechPP = self.zero()
        pmZillCum = self.zero()
        pmZillPP = self.zero()
        pmPourPB = self.zero()
        tierPM = self.zero()
        zillTot = self.zero()
        pbSortMatsPP = self.zero()
        pbSortSurrPP = self.zero()
        pbSortDthPP = self.zero()
        

        # Calcul des PM au temps 0 
        valAccrbPP[:,0,:] = pbAcquPP[:,0,:] * AExn[:,0,:] 
        
        tierPM[:,0,:] = (1/3) * np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] + precPP[:,0,:] - valNetPP[:,0,:], 0)
            
        zillTot[:,0,:] = np.minimum(alpha[:,0,:] * prInventPP[:,0,:] * axn[:,0,:], np.maximum(valSumAss[:,0,:] - valNetPP[:,0,:] + provGestPP[:,0,:], 0))
            
        zill[:,0,:] = np.where((tierPM[:,0,:] <= zillTot[:,0,:]) & (nbtete[:,0,:] != 2), tierPM[:,0,:], zillTot[:,0,:])
        
        mathResPP[:,0,:] = np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] - valNetPP[:,0,:] + precPP[:,0,:] - zill[:,0,:], 0 )

        provTechPP[:,0,:] = mathResPP[:,0,:] - provGestPP[:,0,:] - precPP[:,0,:] + zill[:,0,:]
        
        pmZillPP[:,0,:] = provTechPP[:,0,:] - zill[:,0,:]
        
        
        for i in range(1,self.shape[1]):

#Définition des variables des actifs            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:] - nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseD[:,i,:]))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxyD[:,i,:]))
            
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:] - nbrMaturities[:,i,:]


#Définition des variables des réduites
            nbrPupMaturities[:,i,:]=nbrPupsIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPupIfSM[:,i,:]=nbrPupsIf[:,i-1,:] - nbrPupMaturities[:,i,:]
            
            nbrPupDeath[:,i,:]=nbrPupIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseTiming*lapse[:,i,:]))
            
            nbrPupSurrender[:,i,:]=nbrPupIfSM[:,i,:]*lapse[:,i,:]*(1-(lapseTiming*qxy[:,i,:]))
            
            nbrPupsIf[:,i,:]=nbrPupsIf[:,i-1,:]-nbrPupDeath[:,i,:]-nbrPupSurrender[:,i,:] - nbrPupMaturities[:,i,:] + nbrNewRed[:,i,:]


# Variable permettant le calcul des reserves et pb

            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

            valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] 
            
            tierPM[:,i,:] = (1/3) * (np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0))
            
            zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:], 0))
            
            zill[:,i,:] = np.where((tierPM[:,i,:] <= zillTot[:,i,:]) & (nbtete[:,i,:] != 2), tierPM[:,i,:], zillTot[:,i,:])
            
            mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )
            
            provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]
            
            pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
            pbSortSurrPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:] * AExn[:,i,:]
            
            pbSortDthPP[:,i,:] = pbCalcPP[:,i-1,:] * isActive[:,i,:]



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



# Sauvegarde des variables concernant les PM
 # Montant de PB à affecter par police
        self.pbCalcPP = pbCalcPP
  # PB acquise des polices actives
        self.pbAcquPP = pbAcquPP
# PB dfdonnée par police en cas de maturité     
        self.pbSortMatsPP = pbSortMatsPP
# PB donnée par police en cas de rachat
        self.pbSortSurrPP = pbSortSurrPP
# PM utilisée pour le calcul de la PB
        self.pmPourPB = pmPourPB
# PM Zillmérisée cumulée 
        self.pmZillCum = pmZillCum
# Provisions technique par police 
        self.provTechPP = provTechPP
# Reserves mathématiques par polices       
        self.mathResPP = mathResPP
# Valeur actualisée de la PB 
        self.valAccrbPP = valAccrbPP
# PB incorporée par polices       
        self.pbIncorPP = pbIncorPP
# Provision zillmérisée par police     
        self.pmZillPP = pmZillPP
# Zillmérisation 
        self.zill = zill
# Zillmérisation en comptant le (1/3) de la pm comme zill       
        self.zillTot = zillTot
# Tiers de la pm comptée comme zill       
        self.tierPM = tierPM
# PB donnée par police en cas de décès
        self.pbSortDthPP = pbSortDthPP



# Met un vecteur de 1 et 0 (1 si la police possède moins de 12 mois)
    def pmFirstYear(self):
        vec = self.one() * 12
        mask = self.durationIf() <= 12
        vec[mask] = self.durationIf()[mask]
        return vec
 
# Arrondi des tables afin d'obtenir taux pb (table rdt est). Le taux PB va également dépendre du taux d'intêret 
    def txPartPB(self):
        rate = (1+self.pbRate())**12 - 1
        rate = (1+rate)**(1/12) - 1

        # ligne à supprimer pour corriger !! il ne faut pas arrondir ce taux
        rate = np.round(rate, decimals = 6)
        
        txInt = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()/100
        return np.maximum(0, rate - txInt)
    
# =============================================================================
    ### CALCUL DES PREMIUMS
# =============================================================================

# Prime complémentaire qui va dépendre de la modalité et du tarif. Pourquoi POLPRCPLA est présent nulle part ici ?
    def annRider(self):
        
        # Prime complémentaire pour les mixtes
        primeCompl = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5']\
                      + self.p['POLPRCPL6'] + self.p['POLPRCPL9'])
            
        # Prime complémentaire pour les taux d'interet inférieur à 2.5 et age dépassant 65
        primeCompl2 = (self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL9'])
        
        # prime complémentaire pour les produits mixtes à 2 têtes (A SUPPRIMER POUR CORRIGER car il n'y a pas PA+ ici) !!
        mask22 = (self.p['POLNBTETE'] == 2)
        primeCompl[mask22] = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5'] + self.p['POLPRCPL6'])[mask22]   
        primeCompl2[mask22] = (self.p['POLPRCPL3'] + self.p['POLPRCPL4'])[mask22]
        
        # prime complémentaire pour pour les modalités 10
        mask10 = (self.p['PMBMOD'] == 10)
        primeCompl[mask10] = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5'] \
                              + self.p['POLPRCPL6'] + self.p['POLPRCPL8'] + self.p['POLPRCPL9'])[mask10]   
            
        primeCompl2[mask10] = primeCompl[mask10]
        primeCompl = primeCompl[:,np.newaxis,np.newaxis] * self.one()
        primeCompl2 = primeCompl2[:,np.newaxis,np.newaxis] * self.one()
        
        # Condition sur la limite d'age qui va dépendre de la modalité et du tarif, ici du taux t'intêret
        maskA = ((self.p['POLINTERG'] <= 2)[:,np.newaxis,np.newaxis] * self.one()).astype(bool)
        maskB = ((self.p['POLINTERG'] > 2)[:,np.newaxis,np.newaxis] * self.one()).astype(bool)
        
        maskCPL1 = (self.age() <= self.ageLimiteCPL1 ).astype(bool)
        maskCPL2 = (self.age() <= self.ageLimiteCPL2).astype(bool)
  
        total = self.zero()
        conditions = [ maskA * maskCPL1, maskA * maskCPL2, maskB * maskCPL1]
        choices = [primeCompl, primeCompl2, primeCompl]
        return np.select(conditions, choices, default=0)

#Retourne les primes totales perçues. Il faut prendre en compte les primes pouvant être indexé, et rajouté les autres primes sans indexation. POLPRCPLA pas dans ANNRIDER pourquoi ?
    def totalPremium(self):
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])/self.frac()
        premCompl = self.annRider() / self.frac()
        prem=(premInc*self.indexation() + premCompl) * self.nbrPolIfSM * self.isPremPay()
        # prime à 0 pour les modalités 6 et 7
        mask67 = self.mask([6,7])
        prem[mask67] = 0
        return prem


# =============================================================================
    ### CALCUL DES CLAIMS
# =============================================================================
# retourne la somme assurée avec le bon format
    def sumAss(self): 
        return self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one() 

# Calcul des primes d'inventaire annuelle (PA'')
    def prInventaire(self):
        loading = self.p['aquisitionLoading'][:,np.newaxis, np.newaxis]*self.one()   
        fraisFract = self.p['fraisFract'][:,np.newaxis, np.newaxis]*self.one()  
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])
        premInc = premInc * self.indexation()
        prInventaire = premInc * (1-loading) / fraisFract
        
        # Modalité 10 ont une prime d'inventaire de 0 (A SUPPRIMER POUR CORRIGER)
        mask = (self.p['POLSIT']==4) | (self.p['POLSIT']==9) | (self.p['PMBMOD'].isin([10])) 
        prInventaire[mask] = self.zero()[mask]
        return prInventaire
        
# Calcul des primes pures PR PURE PP
    def prPure(self):
        gestLoading = self.p['gestionLoadingSA'][:,np.newaxis, np.newaxis]*self.one() 
        capital = self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one()  
        prInvent = self.prInventaire()
        ppure = prInvent - gestLoading * capital
        mask = (self.p['POLSIT']==4) | (self.p['POLSIT']==9)
        ppure[mask] = self.zero()[mask]
        return ppure
        
# Valeur actualisée des primes nettes
    def valNetPrem(self):
        premNet = self.prPure()
        axn = self.axn
        valNetPrem = premNet * axn
        # mod6 et 7 valnetPrem = 0
        mask = self.p['PMBMOD'].isin([6,7])
        valNetPrem[mask] = self.zero()[mask]
        return valNetPrem

# Valeur actualisé SA (Net single premium value) AExn * capital
    def valSaPP(self):
        # mask ici car au moment de l'échéance de la police, le net Single premium = 0 et non Capital
        mask = self.polTermM() > self.durationIf() 
        valSaPP = self.zero()
        valSaPP[mask] = self.AExn[mask] * self.sumAss()[mask]
        return valSaPP

#Retourne les primes totales sans inforce ni fractionnement
    def annPremPP(self):
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])
        premInc=premInc*self.indexation()
        return premInc + self.annRider() 

#Retourne les provisions pour risque en cours. Reprendre une méthode commune à tout le portefeuille pour calculé les risque en cours !!
    def precPP(self):
        mask10 = self.mask([10])
        annPremPP = self.annPremPP()
    # pourquoi prend-on en compte les AnnRider pour les mod10 ?
        annPremPP[mask10] = self.annRider()[mask10]
        fraisFract = self.p['fraisFract'][:,np.newaxis, np.newaxis]*self.one() 
        loading = self.p['aquisitionLoading'][:,np.newaxis, np.newaxis]*self.one()  
        premForREC = annPremPP / fraisFract / (1+loading)
        precPP = premForREC * self.timeBeforeNextPay()/self.frac()
        
# calcul de precPP pour les modalité 10 (il faut une même méthode pour tout les risques en cours du portefeuille) !!
        frek=self.frac()
        premCompl = self.annRider()/frek 
        riderIncPP=premCompl*self.isPremPay()
        riderIncPP2=premCompl
        precPP10 = self.zero()
        
        for i in range(1,self.shape[1]):
            precPP10[:,i,:]=precPP10[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
        
        precPP[mask10] = precPP10[mask10]
        
        return precPP * self.isActive()

# retourne la provision mathèmatique de gestion
    def pmgSA(self):
        tauxPM =self.p['gestionLoadingSA'][:,np.newaxis, np.newaxis]*self.one()  
        return tauxPM * self.axn 

# Provision de gestion calculée sans pb
    def provGestPP(self):
        pm = self.pmgSA()  * self.sumAss() - self.axn * (self.prInventaire() - self.prPure())
        pm[self.p['PMBMOD'].isin([6,7])] = self.zero()[self.p['PMBMOD'].isin([6,7])]
        return pm


# claim complémentaire par police RIDER INC PP
    def riderIncPP(self):
        return (self.annRider() / self.frac()) * self.isPremPay()


# calcul du taux de sinistralité complémentaire
    def riderCRate(self):
        annRider = self.annRider()
        
        mask2 = ((self.p['PMBTXINT'] > 2)[:,np.newaxis, np.newaxis]*self.one()).astype(bool)
        mask0 = ((self.p['PMBTXINT'] <= 2)[:,np.newaxis, np.newaxis]*self.one()).astype(bool)
        maskCPL1 = (self.age() <= self.ageLimiteCPL1 ).astype(bool)
        maskCPL2 = (self.age() <= self.ageLimiteCPL2).astype(bool)
        
        primeIPT = self.p['POLPRCPL1'][:,np.newaxis, np.newaxis]*self.one() 
        primeTPLacc = self.p['POLPRCPL3'][:,np.newaxis, np.newaxis]*self.one() 
        primeExoIG = self.p['POLPRCPL4'][:,np.newaxis, np.newaxis]*self.one() 
        primeExoRenteIG = self.p['POLPRCPL5'][:,np.newaxis, np.newaxis]*self.one() 
        primeHospi = self.p['POLPRCPL6'][:,np.newaxis, np.newaxis]*self.one() 
        primeAccPA = self.p['POLPRCPL9'][:,np.newaxis, np.newaxis]*self.one() 
        primeDcAdulte = self.p['POLPRCPL8'][:,np.newaxis, np.newaxis]*self.one() 
        
        txIPT = self.ipt()
        txAcc = self.dcAccident()
        txExo = self.exo()
        txExoRenteIG = self.itt()
        txHospi = self.hospi()
        txAccPA = self.dcAccident()
        
        # taux jamais calculé, voici la correction
        # txDcAdulte = self.dcAccident() 
        txDcAdulte = self.one()
        
        tx = self.zero()
  
        cond1 = primeIPT * txIPT + primeTPLacc * txAcc + primeExoIG * txExo + primeExoRenteIG * txExoRenteIG + primeHospi * txHospi + primeAccPA * txAccPA
        cond2 = primeAccPA * txAccPA
        cond3 = primeTPLacc * txAcc + primeExoIG * txExo + primeAccPA * txAccPA

        conditions = [ mask2 & maskCPL1, mask2 & maskCPL2 , mask0 & maskCPL1, mask0 & maskCPL2]
        choices = [cond1, cond2, cond1, cond3]
        tx[annRider>0] = np.select(conditions, choices, default=0)[annRider>0] / annRider[annRider>0]
        
        # traitement modalité 10
        mask10 = self.p['PMBMOD'].isin([10])
        
        # ce taux est à 100 dans prophet A SUPPRIMER POUR CORRIGER
        txExoRenteIG[mask10] = self.one()[mask10]
        
        cond4 = primeExoIG * txExo + primeExoRenteIG * txExoRenteIG + primeDcAdulte * txDcAdulte
        tx[mask10] = cond4[mask10] / annRider[mask10]
        return tx

# Coût des complémentaires
    def riderCostPP(self): 
        return self.riderIncPP() * self.riderCRate()
     
 
# Calcul des claim complémentaire
    def claimCompl(self):
        maskPA = (self.p['POLPRCPLA'] != 0)
        maskNpa = (self.p['POLPRCPLA'] == 0)
        riderCoutgo = self.zero()
        riderCoutgo[maskPA] = self.riderCostPP()[maskPA] * self.nbrPolIfSM[maskPA] + self.nbrDeath[maskPA] * self.capPA()[maskPA]
        riderCoutgo[maskNpa] = self.riderCostPP()[maskNpa] * self.nbrPolIfSM[maskNpa] 
        return riderCoutgo
    
    
# calcul des benefices en cas de maturité par police
    def matBenPP(self):
        return self.pbAcquPP + self.sumAss() + self.pbSortMatsPP
    
 # calcul des sorties total en cas de maturité 
    def maturity(self):
        noMats = self.nbrNewMat
        matBenPP = self.matBenPP()
        matOutgo = self.zero()

        for i in range(1,self.shape[1]):
            matOutgo[:,i,:] = matBenPP[:,i-1,:] * noMats[:,i,:] 
        
        return matOutgo
    
    
# calcul de la valeur en cas de lapse
    def surrValPP(self):
        pb = self.pbSortSurrPP
        pm = self.mathResPP
        surrValue = self.zero()
        # le rachat n'est possible qu'après 3 ans
        surrValue[self.durationIf() > 36] = np.maximum(pm, pb)[self.durationIf() > 36]
        # Calcul des surrender outgo pour les modalité 6 et 7. Pourquoi la valeur change pour ces modalité ?
        pmzill = self.pmZillPP
        surrValue[self.mask([6,7])] = pmzill[self.mask([6,7])]
        return surrValue
    
    
# calcul des sorties en cas de rachat
    def surrender(self):
        return self.surrValPP() * self.nbrSurrender
    
# retourne un vecteur de 1 à 12 selon la duration de la police, si + élevé de 12 mois alors 12
    def firstYear(self):
        dur = self.durationIf()
        dur[dur>12] = 12 
        return dur

#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        return (self.sumAss() + self.pbAcquPP) * self.nbrDeath



# =============================================================================
    ### CALCUL DES EXPENSES
# =============================================================================

# calcul des reserves par police
    def mathResBA(self):
        return np.maximum(self.valSaPP() + self.valAccrbPP + self.provGestPP() + self.precPP() - self.valNetPrem() - self.zill, 0) 

# reserves inforce
    def provMathIf(self):
        return self.mathResPP * self.nbrPolIf
    

# Dotation PB inforce actualisé
    def dotationPB(self):
        return self.pbCalcPP * self.AExn * self.nbrPolIf

# Calcul de l'évolution du fond de PB
    def fondPB(self):
        dotationPB = self.dotationPB()
        fondPB = self.zero()
        reprisePB = self.zero()
 
        for i in range(1,self.shape[1]):
            reprisePB[:,i,:] = fondPB[:,i-1,:]
            fondPB[:,i,:] =  fondPB[:,i-1,:] + dotationPB[:,i,:] - reprisePB[:,i,:]
        return fondPB
    
# Reprise pour incorporation de PB
    def reprisePB(self):
        return np.roll(self.fondPB(), 1, axis = 1)
    
# Reprise sur fond de PB suite à une maturité  
    def repPbMats(self):
        return self.zero()
    
# pb incorporée actualisé inforce
    def pbIncorpIF(self):
        AExn = np.roll(self.AExn, 1, axis = 1)
        return self.pbIncorPP * AExn * self.nbrPolIfSM
    
    
# coût de la pb sur sorties
    def pbSortie(self):
        pbSortMatsPP = np.roll(self.pbSortMatsPP, 1, axis = 1)
        # A mon avis pbSortSurr et pbSortDth ne devraient pas être à 0, ce sont les pb donnée en cas de sortie pour décès ou lapse (?) 
        pbSortSurrPP = self.zero()
        pbSortDthPP = self.zero()
        valueLapse = pbSortDthPP * self.nbrDeath + pbSortSurrPP * self.nbrSurrender + pbSortMatsPP * self.nbrNewMat
        value = pbSortDthPP * self.nbrDeath + pbSortMatsPP * self.nbrNewMat
        value[self.surrValPP() > 0] = valueLapse[self.surrValPP() > 0]
        return value
    
# Zillmérisation inforce
    def valZillIf(self):
        return  self.zill * self.nbrPolIf
    
# calcul des provisions techniques en cours, inforce
    def provTechIf(self):
        return self.provTechPP * self.nbrPolIf 
    
# diminution de la provision non zilmérisée à la maturité du contrat 
    def tresRldMat(self):
        return np.roll(self.provTechPP, 1, axis = 1) * self.nbrNewMat
     
#  calcul des provisions techniques ajustée (PROV_TECH_AJ)
    def provTechAj(self):
        provTechAj = self.zero()
        provTechIf = self.provTechIf()
        primeInvest = self.prPure() * self.nbrPolIfSM * self.isPremPay() / self.frac()
        riderCoutgo = self.claimCompl()
        tresRldMat = self.tresRldMat()
        pbIncorpIf = self.pbIncorpIF()
        
        for i in range(1,self.shape[1]):
            provTechAj[:,i,:] = provTechIf[:,i-1,:] + pbIncorpIf[:,i,:] + primeInvest[:,i,:] - riderCoutgo[:,i,:] - tresRldMat[:,i,:]
        return provTechAj
    
    
# provision de gestion en cours 
    def provGestIf(self):
        return self.provGestPP() * self.nbrPolIf


  # calcul des intêret techniques crédités (INT_CRED_T) 
    def totIntCred(self):
        
# intêrets techniques crédité        
        intCredT = (self.txInt()-1) * self.provTechAj()
        intCredT[:,0,:] = 0
        
# intêrets crédités sur provision de gestion en cours
        intCredPMG = np.roll(self.provGestIf(), 1, axis = 1) * (self.txInt()-1)
        
# Intêrets crédités sur zillmérisation     
        intCredZil = (self.txInt()-1) * np.roll(self.valZillIf(), 1, axis = 1)
        intCredZil[:,0,:] = 0
        
        return intCredT + intCredPMG - intCredZil
    
    
# Arrondi des tables ACTU.FAC afin d'obtenir mUfii (table rdt est)
# méthode suivante à supprimer, il n'y a aucune raison d'arrondir le taux d'intêret !!
    def mUfii(self):
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        rate = (1+rate)**(1/12) - 1
        return rate
 # A remplacer par:
     # def mUfii(self):
     #    return self.rate()
# Ou changer le nom des mUfii par self.rate()



# # loop pour calculer les reserves pour expense ADJ_MATHRES2
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
          noMat = self.nbrNewMat
 
          # fonction existantes
          fMathResIF = self.provMathIf() + self.fondPB()
          provMathIf = self.provMathIf()
          riderCoutgo = self.claimCompl()
          pbIncorpIF = self.pbIncorpIF()
          premInc = self.totalPremium()

          fondPB = self.fondPB()
          mUfii = self.mUfii()
          repPbMats = self.repPbMats()
          premInvest = self.prPure() * self.nbrPolIfSM * self.isPremPay() / self.frac()
          # les primes investies sont à 0 pour les modalité à primes unique
          premInvest[self.p['PMBMOD'].isin([6,7])] = self.zero()[self.p['PMBMOD'].isin([6,7])]
          unitExp = self.unitExpense()
          reprisePB = self.reprisePB()
          dotationPB = self.dotationPB()
          pbSortie = self.pbSortie()
          totIntCred = self.totIntCred() 
          txReserve = self.fraisGestionPlacement()
          mathresPP = self.mathResPP  
          totComm = self.totalCommissions()
          monthPb = self.one() - self.allocMonths()
          isActive = self.isActive()
      
          for i in range(1,self.shape[1]):
            
              resReldMatTEMP =  (fondPB[:,i-1,:] + rfinAnn[:,i-1,:])
            
              resReldMat[:,i,:] = np.divide(resReldMatTEMP, (nbrPolIf[:,i-1,:]), out=np.zeros_like(resReldMatTEMP), where=(nbrPolIf[:,i-1,:])!=0)\
                  * noMat[:,i,:] + mathresPP[:,i-1,:] * noMat[:,i,:] 
            
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

print("Class MI--- %s sec" %'%.2f'%  (time.time() - start_time))

# =============================================================================
### TEST ET FONCTIONALITES
# =============================================================================



# pol=FU()
# pol=AX()
# pol = HO()
# pol=PR()
# pol = EP()
# pol=VE()
# pol=MI()
# pol=TE()

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


