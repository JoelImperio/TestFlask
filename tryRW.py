from Portefeuille import Portfolio
import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()



class MyFU(Portfolio):
    mods=[8,9]
    ageMax=65
    complPremium=60
#Lapse timing = 1 correspond aux lapse en début de mois et décès en fin de mois
#Nous pensons que l'hypothèse meilleure serait lapse et décès en milieu de mois soit lapseTiming=0.5
#    lapseTiming=0.5
    lapseTiming=1
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loop()

#Cette Loop permets de passé sur l'entier des périodes de projection et renvoie l'ensemble des variables récusrives
    def loop(self):
        
        nbrPolIf=self.one()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrPolIfSM=self.zero()
        
        matRate=self.zero()
        matRate[self.polTermM()+1==self.durationIf()]=1
        
        qxy=self.qxyExpMens()
        lapse=self.lapse()
        lapseTiming=1
        
        
        for i in range(1,self.shape[1]):
            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapse[:,i,:]*(1-lapseTiming)))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxy[:,i,:]*lapseTiming))

            
            
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]
                        
            
        self.nbrPolIf=nbrPolIf
        self.nbrPolIfSM=nbrPolIfSM
        self.nbrMaturities=nbrMaturities
        self.nbrDeath=nbrDeath
        self.nbrSurrender=nbrSurrender
        
        
        return self


#Durée du contrat en mois
    def polTermM(self):
        
        entryAge1= np.copy(self.p['Age1AtEntry'].to_numpy())
        
        entryAge2=np.copy(self.p['Age2AtEntry'].to_numpy())
        
        entryAge2[entryAge2==999]=0
        ageAtEntry=np.maximum(entryAge1,entryAge2)
        
        #Nous pensons que cette variante est plus correct car dans le mod 9 la police continue jusqu'à 65 ans du plus jeune assuré
        #Il faut ajouté le code commenté pour prendre en compte le changement
        
#        mod=self.p['PMBMOD'].to_numpy()        
#        entryAge2[entryAge2==0]=999
#        ageAtEntry[mod==9]=np.minimum(entryAge1[mod==9],entryAge2[mod==9])
        
        
        ageAtEntry=ageAtEntry[:,np.newaxis,np.newaxis]*self.one()
        
        ageTerm=self.ageMax*self.one()
        
        polTerm=(ageTerm-ageAtEntry)*12

        return polTerm

    
    def totalPremium(self):
        premInc=self.p['POLPRTOT'][:,np.newaxis,np.newaxis]/self.frac()
        
        prem=premInc*self.nbrPolIfSM*self.isPremPay()
        
        return prem
    
    def premiumCompl(self):
        return (self.complPremium/self.frac())*self.nbrPolIfSM
    
    def purePremium(self):
        return self.p['POLPRDECES'].to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
    def deathClaim(self):
        nbDeath=self.nbrDeath
        capital=self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]
        return nbDeath*capital
    
    def fraisVisiteClaim(self):
        
        claimRate=self.fraisVisite()
        
        premiumCompl=self.premiumCompl()
        
        claim=claimRate*premiumCompl*self.isPremPay()
        
        return claim
           
    
    def totalClaim(self):
        
        return self.deathClaim()+self.fraisVisiteClaim()
    
    def totalCommissions(self):
        
        return self.totalPremium()*self.commissions()

    def unitExpense(self):
        
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        
        coutParPolice=self.fraisGestion()
        
        cost=coutParPolice*inflation*self.nbrPolIfSM
        
        return cost
    
    # Retourne la durée écoulée depuis le dernier paiement de prime   
    def timeBeforeNextPay(self):

        check1 = (self.frac() * (self.durationIf() + 11) /12)
        check2 = np.floor((self.frac() * (self.durationIf() + 11) /12))
 
        elapseTime=(1-(check1-check2))*(1-self.isPremPay())  
        

        elapseTime=np.roll(elapseTime, [-1], axis=1)
#        elapseTime[:,:-1,:]=elapseTime[:,1:,:]
        
        # Le premier mois est à 0
        elapseTime[:,-1,:] = 0
           
        return elapseTime    
    
    def risqueEnCour(self):
        
        elapseTime=self.timeBeforeNextPay()
        
        purePremium=self.purePremium()
        
        risque=purePremium*elapseTime*self.nbrPolIf
        
        risque=np.roll(risque,[1],axis=1)
        risque[:,0,:]=0
              
        return risque


    def adjustedReserve(self):
        
        
        purePremium=self.purePremium()*self.nbrPolIfSM*self.isPremPay()
        
        pureRiskPremium=self.totalPremium()-purePremium
        
        riderCost=self.fraisVisiteClaim()
        
        risqueEnCour=self.risqueEnCour()
        
        
        reserve=purePremium-pureRiskPremium-riderCost+risqueEnCour
        
        return reserve
    
    def reserveExpense(self):
        
        reserve=self.adjustedReserve()
        
        tauxFraisGestion=self.fraisGestionPlacement()
        
        return reserve*tauxFraisGestion

        
    def totalExpense(self):
        
        return self.unitExpense()+self.reserveExpense()
    
        
      
        
    
        

##############################################################################################################################
#############ICI pour faire des tests sur la class
##############################################################################################################################
      
def testerFU(self):
    return self


pol=MyFU()


pol.ids([1690202])
#pol.mod([9])

#a=pol.polTermM()
#b=pol.isActive()
#c=pol.durationIf()
#d=pol.loop()
#e=pol.nbrPolIf
#f=pol.nbrPolIfSM
#g=pol.nbrMaturities
#h=pol.nbrDeath
#i=pol.nbrSurrender
#j=pol.totalPremium()
#k=pol.nbrDeath
#l=pol.nbrMaturities
#m=pol.nbrPolIf
#n=pol.nbrPolIfSM
#o=pol.nbrSurrender
#p=pol.deathClaim()
#q=pol.fraisVisiteClaim()
#r=pol.totalClaim()
#s=pol.totalCommissions()
t=pol.unitExpense()
u=pol.risqueEnCour()
v=pol.adjustedReserve()
w=pol.reserveExpense()
x=pol.totalExpense()

#Analyse un cas

monCas=u

zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z.to_csv(r'check.csv')




print("Class FU--- %s sec" %'%.2f'%  (time.time() - start_time))


#a=pol.p.PMBCAPIT.unique()


