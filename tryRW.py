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
        
        
        for i in range(1,self.shape[1]):
            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapse[:,i,:]*0.5))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxy[:,i,:]*0.5))
            
            
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

#Retourn un 1 tant que la police est active et 0 lorsque dépasse le terme   
    def isActive(self):
        term=self.polTermM()
        dur=self.durationIf()
        
        active=self.one()
        
        active[dur>term]=0
        
        return active
    
    def premium(self):
        premInc=self.p['POLPRTOT'][:,np.newaxis,np.newaxis]/self.frac()
        
        prem=premInc*self.nbrPolIfSM*self.isPremPay()
        
        return prem
        

##############################################################################################################################
#############ICI pour faire des tests sur la class
##############################################################################################################################
      
def testerFU(self):
    return self


pol=MyFU()


#z=pol.ids([896002])


#a=pol.polTermM()
#b=pol.isActive()
#c=pol.durationIf()
#d=pol.loop()
#e=pol.nbrPolIf
#f=pol.nbrPolIfSM
#g=pol.nbrMaturities
#h=pol.nbrDeath
#i=pol.nbrSurrender
j=pol.premium()

a=np.sum(j,axis=0)








print("Class FU--- %s sec" %'%.2f'%  (time.time() - start_time))


