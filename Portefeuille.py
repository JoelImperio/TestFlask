import pandas as pd
import numpy as np
from Parametres import Hypo, allRuns,tableExperience
from MyPyliferisk import MortalityTable
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()


##############################################################################################################################
#Création de la class Portefeuille
##############################################################################################################################

class Portfolio(Hypo):

    ageNan=999
    
#Lapse timing = 1 correspond aux lapse en début de mois et décès en fin de mois
#Nous pensons que l'hypothèse meilleure serait lapse et décès en milieu de mois soit lapseTiming=0.5
#    lapseTiming=0.5
    lapseTiming=1
 
    def __init__(self,runs=allRuns, \
                 myPortfolioNew=True, mySinistralityNew=True,myLapseNew=True,myCostNew=True,myRateNew=True):  
        super().__init__(Run=runs,\
             PortfolioNew=myPortfolioNew, SinistralityNew=mySinistralityNew,LapseNew=myLapseNew,CostNew=myCostNew,RateNew=myRateNew)

##############################################################################################################################
###############################################DEBUT DES METHODES ACTUARIELLES################################################
##############################################################################################################################
    
#Retourne les ages pour l'assuré 1 ou 2 (defaut assuré 1)   
    def age(self,ass=1):

        ageInitial=self.p['Age{}AtEntry'.format(ass)].to_numpy()        
        ageInitial=ageInitial[:,np.newaxis,np.newaxis]
        
        duration=self.durationIf()-1
        duration=(duration-np.mod(duration,12))/12
        
        age=self.zero()       
        age=age+ageInitial         
        age=np.where(age==self.ageNan,age,age+duration)

        return np.copy(age)

#Retourne les qx dimensionné pour une table de mortalité,une expérience (100 = 100% de la table) et pour l'assuré 1 ou 2
    def qx(self,table=tableExperience, exp=100, ass=1):
         
        mt=MortalityTable(nt=table, perc=exp)
        
        aQx=pd.DataFrame(mt.qx).to_numpy()
        
        myAge=(self.age(ass)).astype(int)
        myAge=np.where(myAge>mt.w,mt.w-1,myAge)
        
        myQx=np.take(aQx,myAge)
        
        #Lorsque l'âge est à 999 ans le qx est forcé à 0
        return np.where(self.age(ass) == self.ageNan,0,myQx)
    
#Retourne la probabilité de décès d'expérience
    def qxExp(self,assExp=1):
        
        myQx=self.qx(ass=assExp)*self.dc()
        
        return np.copy(myQx)
    
    
#Retourne la probabilité de décès mensuelle d'expérience pour l'assuré 1 ou 2
    def qxExpMens(self, ass=1):
        
        qx=1-(1-self.qxExp(assExp=ass))**(1/12)
        
        qx[:,0,:] = 0
        
        return qx
    
#Retourn la probabilité jointe de décès mensuelle d'expérience
    def qxyExpMens(self):
        
        qx=self.qxExpMens(ass=1)
        
        qy=self.qxExpMens(ass=2)
        
        return qx+qy-qx*qy

##############################################################################################################################
###############################################DEBUT DES METHODES DE PROJECTION###############################################
##############################################################################################################################
        
#Cette Loop permets de passer sur l'entier des périodes de projection et renvoie l'ensemble des variables récusrives
    def loopNoSaving(self):
        
        nbrPolIf=self.one()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrPolIfSM=self.zero()
        
        matRate=self.zero()
        polTermM=self.polTermM()
        
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
    
#Retourne les risque en cours, soit les primes émises non aquises
    def risqueEnCour(self):
        
        elapseTime=self.timeBeforeNextPay()
        
        purePremium=self.purePremium()
        
        reserve=purePremium*elapseTime*self.nbrPolIf 
                      
        return reserve

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
        return self.claimPrincipal() +self.claimCompl()

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
        
        indexer=self.p['ClassPGG'].unique()
        
        dfPGG=pd.DataFrame(index=indexer,columns=['PGG'])
        
        dfPGG['PGG']=pgg
                      
        return dfPGG




    
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def testerPortfolio():
    return 0
  
#myPolicies=Portfolio(runs=[4,5])
#myPolicies=Portfolio()

#myPolicies.mod([8,9])
#myPolicies.ids([896002])
#myPolicies.groupe(['MI3.5'])

#Les méthodes de la class Portfolio()

#za=myPolicies.age(1)
#zb=myPolicies.qx(table=EKM05i,exp=41.73,ass=2)
#zc=myPolicies.qxExp(assExp=2)
#zd=myPolicies.qxExpMens(ass=2)
#ze=myPolicies.qxyExpMens()
#a=myPolicies.age(ass=2)

print("Class Portefeuille--- %s sec" %'%.2f'%  (time.time() - start_time))


###Visualiser un vecteur np en réduisant une dimension
#data=a
#a=pd.DataFrame(data[:,:,1])

