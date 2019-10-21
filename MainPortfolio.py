import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i
from Main import Hypo
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

##############################################################################################################################
#Création de la class Portefeuille
##############################################################################################################################
 

class Portfolio(Hypo):

    ageNan=999
    tableExperience=EKM05i
    
    def __init__(self):      
        super().__init__()


#####DEBUT DES VARIABLES DE CALCUL DES PROJECTIONS#################################################
    
#Retourne le vecteur des ages pour l'assuré 1 ou 2 (defaut assuré 1)   
    def age(self,ass=1):

        ageInitial=self.p['Age{}AtEntry'.format(ass)].to_numpy()        
        ageInitial=ageInitial[:,np.newaxis,np.newaxis]
        
        duration=self.durationIf()-1
        duration=(duration-np.mod(duration,12))/12
        
        age=self.zero       
        age=age+ageInitial         
        age=np.where(age==self.ageNan,age,age+duration)

        return age

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
    
    def qxExp(self,tableExp=tableExperience, assExp=1):
        
        qx=self.qx(table=tableExp,ass=assExp)*self.dc
        
        return qx
    
    
#Retourn la probabilité de décès mensuelle
    def qxExpMens(self,tableM=tableExperience, expM=100, assM=1):
        
        qx=1-(1-self.qxExp(table=tableM,exp=expM,ass=assM))**(1/12)
        
        qx[:,0,:] = 0
        
        return qx
    
#Retourn la probabilité jointe de décès mensuel
    def qxyExpMens(self,tableXY=EKM05i, expXY=100):
        
        qx=self.qxExpMens(tableM=tableXY, expM=expXY, assM=1)
        
        qy=self.qxExpMens(tableM=tableXY, expM=expXY, assM=2)
        
        return qx+qy-qx*qy
        
       
    
##############################################################################################################################
##############################################################################################################################

def testerPortfolio():
    return 0
    
myRun=[1,5]
#myRun=[0,1,2,3,4,5]


myPolicies=Portfolio(Run=myRun)

#myPolicies.mod([8,9])
#myPolicies.ids([896002])
myPolicies.groupe(['MI3.5'])

#Les fonctions de la class Portfolio()


yj=myPolicies.age(1)
#yk=myPolicies.qx(table=EKM05i, exp=41.73,ass=2)
#yl=myPolicies.qxMens(tableM=EKM05i, expM=41.73,assM=2)
#ym=myPolicies.qxyMens(tableXY=EKM05i, expXY=41.73)


###Visualiser un vecteur np en réduisant une dimension
#data=m
#a=pd.DataFrame(data[:,:,1])
