import pandas as pd
import numpy as np
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
from Portefeuille import Portfolio


#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

#Importation d'une intance de Portfolio
p=Portfolio()

#Création de la class Hypothèse

class Hypo:
    
    __slot__=('un','vide','zero','run','shape')

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
        self.securityMarginMarge=1+self.h.iloc[47,2]
        self.securityMarginBio=1+self.h.iloc[48,2]
        self.inflation=1+self.h.iloc[49,2]

# Retourne une template formaté pour tous les runs    
    def templateAllrun(self):             
        myShape=self.shape
        myShape[2]=(p.shape)[2]
        result=np.zeros(myShape)
        return np.copy(result)
        

# Retourne une template avec les années chaque mois
    def templateAllYear(self):
        
        model=p.template
        model=model.copy()
        model.columns=model.columns.year
        return model.transpose()
    
# Retourne les frais de gestion par police
    def fraisGestion(self):
        
        fixfee=self.h.iloc[43,3]
        
        adminCost=self.templateAllrun()
        
        adminCost[:,:,:4]=fixfee
        adminCost[:,:,4]=fixfee*self.securityMarginMarge
        adminCost[:,:,5]=fixfee*self.securityMarginBio
        #Dimensionner pour les runs en appel    
        adminCost=adminCost[:,:,self.run] 
        
        return adminCost
    
    
    def fraisGestionPlacement(self):
        
        fixfee=self.h.iloc[44,3]

        investCost=self.templateAllrun()
        
        investCost[:,:,:4]=fixfee
        investCost[:,:,4]=fixfee*self.securityMarginMarge
        investCost[:,:,5]=fixfee*self.securityMarginBio
        #Dimensionner pour les runs en appel    
        investCost=investCost[:,:,self.run]
        
        return investCost
    
# Cette fonction retourne un vecteur avec les taux d'intérêt mensuel 
    def rate(self):
      
        rates=self.templateAllrun()       
        model=self.templateAllYear()
        model=model.iloc[:self.shape[1]]
        
        allrates=self.h.iloc[2:6,1:38].transpose()
        
        allrates=pd.merge(model,allrates, left_on=0,right_on=2,how='left')
        allrates=allrates.fillna(0)
        allrates=allrates.iloc[:,2:].to_numpy()
        
        #Conversion en taux mensuel
        allMensualrates=(1+allrates)**(1/12)-1
        allMensualrates=allMensualrates[np.newaxis,:,:]
        
        #Quel run pour quel courbe        
        runBE=[0,5,2,3]
        runRL=1
        runMG=4
        #Remplir la template pour chaque runs        
        rates[:,:,runBE]=allMensualrates[:,:,0,np.newaxis]
        rates[:,:,runMG]=allMensualrates[:,:,1]
        rates[:,:,runRL]=allMensualrates[:,:,2]
        #Dimensionner pour les runs en appel    
        rates[:,:,self.run]
        
        return rates

# Taux de pd annuel pour chaque mois de projection   
    def pbRate(self):
        
        fixratePB=self.h.iloc[39,2]/100
        
        rate=self.rate()
        
        ratesPB=((1+rate)**12-1)-fixratePB
        
        return ratesPB

# Taux de rachat dimensionné pour les runs et polices   
    def laspe(self):

        lapseRates=hyp.h.iloc[23:32,1:12]
        lapseRates.columns = lapseRates.iloc[0]
        lapseRates=lapseRates.drop(lapseRates.index[0])
        lapseRates=lapseRates.set_index('Year')
        
        mySize=list(hyp.un.shape)
        
        dur=p.durationIf()
        dur=dur[:mySize[0],:mySize[1],:mySize[2]]
        
        


    


#####ICI pour faire des tests sur la class##########################################################

myRun=[1,4,5]
#myRun=[0,1,2,3,4,5]
policies=Portfolio(runs=myRun)
policies.mod([8,9])
shape=policies.shape

hyp=Hypo(MyShape=shape, Run=myRun)

###Ce que la classe peut faire

a=hyp.fraisGestion()
#b=hyp.fraisGestionPlacement()
#c=hyp.rate()
#d=hyp.pbRate()

#e=hyp.lapse()



#A mettre en place:
#    - Taux--> e/o
#    - TauxPB--> e/o
#    - frais Gestion --> e/o
#    - frais gestion placement--> e/o
#    - Lapse
#    - Reduction
#    - Sinistralité
#    - Commissions
#    - Sensibilité aux rachats
#    - mortalité d'expérience



