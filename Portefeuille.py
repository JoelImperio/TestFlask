import pandas as pd
import numpy as np
from Parametres import Hypo
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
#Création de la class Portefeuille
##############################################################################################################################
 

class Portfolio(Hypo):

    ageNan=999
    allRuns=[0,1,2,3,4,5]
    tableExperience=EKM05i
    
    def __init__(self,runs=allRuns):  
        super().__init__(Run=runs)


#####DEBUT DES VARIABLES DE CALCUL DES PROJECTIONS#################################################
    
#Retourne le vecteur des ages pour l'assuré 1 ou 2 (defaut assuré 1)   
    def age(self,ass=1):

        ageInitial=self.p['Age{}AtEntry'.format(ass)].to_numpy()        
        ageInitial=ageInitial[:,np.newaxis,np.newaxis]
        
        duration=self.durationIf()-1
        duration=(duration-np.mod(duration,12))/12
        
        age=self.zero()       
        age=age+ageInitial         
        age=np.where(age==self.ageNan,age,age+duration)

        return np.copy(age)

#Retourne un vecteur des qx dimensionné correctement pour une table de mortalité, 
# une expérience (100 = 100% de la table) et pour l'assuré 1 ou 2  
    def qx(self,table=tableExperience, exp=100, ass=1):
         
        mt=MortalityTable(nt=table, perc=exp)
        
        aQx=pd.DataFrame(mt.qx).to_numpy()
        
        myAge=(self.age(ass)).astype(int)
        myAge=np.where(myAge>mt.w,mt.w-1,myAge)
        
        myQx=np.take(aQx,myAge)
        
        #Lorsque l'âge est à 999 ans le qx est forcé à 0
        return np.where(self.age(ass) == self.ageNan,0,myQx)
    
    def qxExp(self,assExp=1):
        
        myQx=self.qx(ass=assExp)*self.dc()
        
        return np.copy(myQx)
    
    
#Retourn la probabilité de décès mensuelle
    def qxExpMens(self, ass=1):
        
        qx=1-(1-self.qxExp(assExp=ass))**(1/12)
        
        qx[:,0,:] = 0
        
        return qx
    
#Retourn la probabilité jointe de décès mensuel
    def qxyExpMens(self):
        
        qx=self.qxExpMens(ass=1)
        
        qy=self.qxExpMens(ass=2)
        
        return qx+qy-qx*qy
        
       
    
##############################################################################################################################
#############ICI pour faire des tests sur la class
##############################################################################################################################

def testerPortfolio():
    return 0


    
#myRun=[1,5]
#myRun=[0,1,2,3,4,5]

#myPolicies=Portfolio(runs=myRun)

#myPolicies.mod([8,9])
#myPolicies.ids([896002])
#myPolicies.groupe(['MI3.5'])

#Les fonctions de la class Portfolio()

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
