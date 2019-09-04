import pandas as pd
import numpy as np
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

 

#Création de la class Portefeuille

class Hypo:
        
    def __init__(self,hy=h,hy1=h1,MyShape=[],Run=[0,1,2,3,4,5], New=True):
        self.run=Run
        self.shape=MyShape
        self.un=np.ones(shape)
        self.vide=np.empty_like(self.un)
        self.zero=np.zeros_like(self.un)
        if New:
            self.h=hy
        else:
            self.h=hy1
 
    def fraisGestion(self):
        coutParPolice=self.h.iloc[43,3]
        
        return coutParPolice



    def rate(self):
       return self.h.iloc[2:6,1:38].transpose()

    


##############################ICI pour faire des tests sur la class##########################################################
from iPortfolio import Portfolio
myRun=[1,5]
policies=Portfolio(runs=myRun)
policies.mod([8,9])
shape=policies.shape

hyp=Hypo(MyShape=shape, Run=myRun)

a=hyp.fraisGestion()
b=hyp.un

for i in range(len(hyp.run)):
    
    z=(hyp.run)[i]
    if z==0:
        b[:,:,i]=b[:,:,i]*a*i
    elif z==1:
        b[:,:,i]=b[:,:,i]*a*i
    elif z==2:
        b[:,:,i]=b[:,:,i]*a*i
    elif z==3:
        b[:,:,i]=b[:,:,i]*a*i
    elif z==4:
        b[:,:,i]=b[:,:,i]*a*i
    elif z==5:
        b[:,:,i]=b[:,:,i]*a*i



        
    

#b=a.iloc[1:,1].to_numpy()
#c=np.repeat(b,12)
#b=Hypo(policies).run
#c=hyp.run
#d=hyp.p
#e=hyp.fixcost()




#Tables :
#-	Actu
#-	Paramfrais: 2 types de frais
#-	Global:mortalité d’expérience, sensibilité aux rachat, taux d’inflation
#-	Rdt-est: taux de PB
#-	Rachat: taux de rachat
#-	Reducs: taux de réduction
#-	Paramgticompl: taux de sinistralité
#-	Paramcomm: commissions ? ou directement dans le portfolio ?
#-  Date de calcul
#
#- Il y a les inputs en lien avec le run 
#- Il y a des inputs généraux




