import pandas as pd
from iPortfolio import portfolio


h=pd.ExcelFile(r'Hypotheses\TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(r'Hypotheses\TablesProphet 2018-12.xls').parse("Hypothèses")
 

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




#Création de la class Portefeuille

class hypo:
        
    def __init__(self,polices,run=0, new=True):
        self.run=run
        if new:
            self.h=h
        else:
            self.h=h1
        self.p=polices

    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def lapse(self):
       return self.h.iloc[2:8,1:38].transpose()

    
    def fixcost(self):
        coutParPolice=self.h.iloc[43,3]
        
        return coutParPolice

policies=portfolio().mod([8,9])
hyp=hypo(policies,run=5)
a=hyp.lapse()
b=hypo(policies).run
c=hyp.run
d=hyp.p
e=hyp.fixcost()







