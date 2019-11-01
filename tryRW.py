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
    premiumLoading=0.2
#Lapse timing = 1 correspond aux lapse en début de mois et décès en fin de mois
#Nous pensons que l'hypothèse meilleure serait lapse et décès en milieu de mois soit lapseTiming=0.5
#    lapseTiming=0.5
    lapseTiming=1
    
    def __init__(self,run=allRuns):
        super().__init__(runs=run)
        self.p=self.mod(self.mods)

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loop()

##############################################################################################################################
###########################################DEBUT DES VARIABLES PRODUITS#######################################################
##############################################################################################################################

#Cette Loop permets de passer sur l'entier des périodes de projection et renvoie l'ensemble des variables récusrives
    def loop(self):
        
        nbrPolIf=self.one()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrPolIfSM=self.zero()
        
        matRate=self.zero()
        polTermM=(self.p['residualTermM']+self.p['DurationIfInitial']).to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        
        matRate[polTermM + 1==self.durationIf()]=1
        
        qxy=self.qxyExpMens()
        lapse=self.lapse()
        lapseTiming=1
             
        for i in range(1,self.shape[1]):
            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapse[:,i,:]*(1-lapseTiming)))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxy[:,i,:]*lapseTiming))

            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]

#Définition des variables récursives
        
        #Nombre de polices actives                                 
        self.nbrPolIf=nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM=nbrPolIfSM
        #Nombre d'échéances de contrat
        self.nbrMaturities=nbrMaturities
        #Nombre de décès
        self.nbrDeath=nbrDeath
        #Nombre d'annulation de contrat
        self.nbrSurrender=nbrSurrender
            
        return self
    
#Retourne les primes des garanties complémentaires    
    def premiumCompl(self):
        return (self.complPremium/self.frac())*self.nbrPolIfSM

#Retourne les primes pures    
    def purePremium(self):
        return self.p['POLPRDECES'].to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
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
            
#Retourne la durée écoulée depuis le dernier paiement de prime   
    def timeBeforeNextPay(self):

        frac=self.frac()
        dur=self.durationIf()
        
        check1 = (frac * (dur + 11) /12)
        check2 = np.floor((frac * (dur + 11) /12))
        
        isNotPremPay=(1-self.isPremPay())
 
        elapseTime=(1-(check1-check2))*isNotPremPay
        
        #Décaler le vécteur d'un temps
        elapseTime[:,:-1,:]=elapseTime[:,1:,:]
        
        # Si la police est finie 0 en dernière place
        mask=(elapseTime[:,-2,:]==0) & (elapseTime[:,-3,:]==0)
        elapseTime[:,-1,:][mask]=0
        # Si 0 mais encore en vigueur on continue la chaine
        mask=(elapseTime[:,-2,:]==0) & (elapseTime[:,-3,:]!=0)
        elapseTime[:,-1,:][mask]=(self.one())[:,-1,:][mask]-(frac[:,-1,:][mask]/12)
        # Si la chaine est en cours on la continu
        mask=(elapseTime[:,-2,:]!=0)
        elapseTime[:,-1,:][mask]=elapseTime[:,-1,:][mask]-(frac[:,-1,:][mask]/12)

        return elapseTime

#Retourne les risque en cours, soit les primes émises non aquises
    def risqueEnCour(self):
        
        elapseTime=self.timeBeforeNextPay()
        
        purePremium=self.p['POLPRDECES'].to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
        
        reserve=purePremium*elapseTime*self.nbrPolIf 
                      
        return reserve

#Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):
        
        prPurePP=((self.p['POLPRTOT']- self.complPremium)*(1-self.premiumLoading)).to_numpy()[:,np.newaxis,np.newaxis]
        pPureEncPP= (prPurePP/self.frac())*self.nbrPolIfSM*self.isPremPay()

        riderCost=self.fraisVisiteClaim()
        
        risqueEnCour=self.risqueEnCour()
        risqueEnCour=np.roll(risqueEnCour,[1],axis=1)
        risqueEnCour[:,0,:]=0       
        
        reserve=np.maximum(pPureEncPP-riderCost+risqueEnCour,0)
        
        return reserve

#Retourne les coûts de gestion des placements appliqué sur les réserves   
    def reserveExpense(self):
        
        reserve=self.adjustedReserve()
        
        tauxFraisGestion=self.fraisGestionPlacement()
        
        return reserve*tauxFraisGestion

#Retourne le coût par police
    def unitExpense(self):
        
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        
        coutParPolice=self.fraisGestion()
        
        cost=coutParPolice*inflation*self.nbrPolIfSM
        
        return cost
   
##############################################################################################################################
###########################################DEBUT DES COMPOSANTES DU BEL#######################################################
##############################################################################################################################

#Retourne les primes totales perçues
    def totalPremium(self):
        premInc=self.p['POLPRTOT'][:,np.newaxis,np.newaxis]/self.frac()
        
        prem=premInc*self.nbrPolIfSM*self.isPremPay()
        
        return prem

#Retourne le total des sinistres payés  
    def totalClaim(self):  
        return self.deathClaim()+self.fraisVisiteClaim()

#Retourne le total des commissions payées
    def totalCommissions(self):        
        return self.totalPremium()*self.commissions()

#Retourne les dépense totales        
    def totalExpense(self):
        return self.unitExpense()+self.reserveExpense()

#Retourne la meilleure estimation des engagements    
    def BEL(self):
        
        interestRates=1+self.rate()       
        premium=self.totalPremium()
        claim=self.totalClaim()
        expense=self.totalExpense()
        commission=self.totalCommissions()
        
        bel=self.zero()
              
        for t in range(1,self.shape[1]+1):
            
            bel[:,-t,:]=(bel[:,-t+1,:]+claim[:,-t+1,:]+expense[:,-t+1,:]+commission[:,-t+1,:]-premium[:,-t+1,:])/interestRates[:,-t+1,:]
            
        return bel

##############################################################################################################################
###########################################DEBUT DU CALCUL DE LA PGG#######################################################
##############################################################################################################################     

    def PGG(self):
        
        pm=np.sum(self.p['PMbasePGG'].to_numpy())
        
        bel=np.sum(self.BEL(), axis=0)[0,:]
        
        maxBel=max(bel)
        
        pgg= max(0,maxBel-pm)
              
        return pgg
  

##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def testerFU(self):
    return self

pol=FU()
#pol=MyFU(run=[4,5])

#pol.ids([2142501])
#pol.mod([9])
#pol.modHead([9],2)

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
#l=pol.adjustedReserve()
#m=pol.reserveExpense()
#n=pol.unitExpense()
#o=pol.totalPremium()
#q=pol.totalClaim()
#r=pol.totalCommissions()
#s=pol.totalExpense()
#t=pol.BEL()

#bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()


print("Class FU--- %s sec" %'%.2f'%  (time.time() - start_time))

##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################
def testerCas(self):
    return self

#monCas=y
#
#zz=np.sum(monCas, axis=0)
#zzz=np.sum(zz[:,0])
#z=pd.DataFrame(monCas[:,:,0])
#z.to_csv(r'check.csv')

#Visualiser une dimension d'un numpy qui n'apparait pas

#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])






