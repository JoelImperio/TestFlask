import pandas as pd
import numpy as np
import os, os.path
import ast
path = os.path.dirname(os.path.abspath(__file__))
 

#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

def eval_code(code):
    parsed = ast.parse(code, mode='eval')
    fixed = ast.fix_missing_locations(parsed)
    compiled = compile(fixed, '<string>', 'eval')
    eval(compiled)

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
 
    def ifsRun(self,choiceForEachRun):
        
        adminCost=self.h.iloc[43,3]*(self.un)
        SecurityMarginMarge=1+self.h.iloc[47,2]
        SecurityMarginBio=1+self.h.iloc[48,2]
        
        
        c=self.un
        listeDesRuns=self.run
        
        for i in range(len(listeDesRuns)):
            z=listeDesRuns[i]
            z=z*(self.un)
            condlist = [z[:,:,i]==0,z[:,:,i]==1,z[:,:,i]==2,z[:,:,i]==3,z[:,:,i]==4,z[:,:,i]==5]
            c[:,:,i]=np.select(condlist, eval(choiceForEachRun))
        return c
    
    def fraisGestion(self):
        
        choiceForEachRun='[adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i]*SecurityMarginMarge,adminCost[:,:,i]*SecurityMarginBio]'
        
        return self.ifsRun(choiceForEachRun)
    
    
    def fraisGestionPlacement(self):
    
        choiceForEachRun='[adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i]*SecurityMarginMarge,adminCost[:,:,i]*SecurityMarginBio]'
    
        return self.ifsRun(choiceForEachRun)




    def rate(self):
       return self.h.iloc[2:6,1:38].transpose()

    


##############################ICI pour faire des tests sur la class##########################################################
from iPortfolio import Portfolio
#myRun=[1,5]
myRun=[0,1,2,3,4,5]
policies=Portfolio(runs=myRun)
policies.mod([8,9])
shape=policies.shape

hyp=Hypo(MyShape=shape, Run=myRun)

a=hyp.fraisGestion()
b=hyp.fraisGestionPlacement()




#c=hyp.un 
#for i in range(len(hyp.run)):
#    z=(hyp.run)[i]
#    z=z*b
#    condlist = [z[:,:,i]==0,z[:,:,i]==1,z[:,:,i]==2,z[:,:,i]==3,z[:,:,i]==4,z[:,:,i]==5]
#    choicelist = [b[:,:,i]*a*i,b[:,:,i]*a*i,b[:,:,i]*a*i,b[:,:,i]*a*i,b[:,:,i]*a*i,b[:,:,i]*a*i]
#    c[:,:,i]=np.select(condlist, choicelist)


#b=a.iloc[1:,1].to_numpy()
#c=np.repeat(b,12)
#b=Hypo(policies).run
#c=hyp.run
#d=hyp.p
#e=hyp.fixcost()


#A mettre en place:
#    - Taux
#    - TauxPB
#    - Sinistralité
#    - Lapse
#    - Reduction
#    - frais Gestion v
#    - frais gestion placement
#    - Commissions


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




