import pandas as pd
import numpy as np
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

 

#Création de la class Portefeuille

class Hypo:
        
    def __init__(self,MyShape=[],Run=[0,1,2,3,4], New=True):
        self.run=Run
        self.shape=MyShape
        if New:
            self.h=h
        else:
            self.h=h1
    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def rate(self):
       return self.h.iloc[2:6,1:38].transpose()

    
    def fixcost(self):
        coutParPolice=self.h.iloc[43,3]
        
        return coutParPolice

##############################ICI pour faire des tests sur la class##########################################################
from iPortfolio import Portfolio
shape=Portfolio().mod([8,9]).shape

hyp=Hypo(MyShape=shape,Run=5)
a=hyp.rate()

b=a.iloc[1:,1].to_numpy()
c=np.repeat(b,12)
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




