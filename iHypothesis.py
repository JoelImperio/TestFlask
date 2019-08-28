import pandas as pd 


h=pd.ExcelFile(r'Hypotheses\TablesProphet 2018-12.xls').parse("Hypothèses")
 

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
    
    tout=h
    
    def __init__(self,runs):
        self
        self.run=runs
    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def lapse(self):
       return h.iloc[2:8,1:38].transpose()
   
    def getRuns(self):
        return self.run


z=hypo(5).lapse()
zz=hypo(5).tout
zzz=hypo(5).run






