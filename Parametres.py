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

#Création de la class Portefeuille

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

#Retourne une template formaté pour tous les runs    
    def templateAllrun(self):             
        myShape=self.shape
        myShape[2]=(p.shape)[2]
        result=np.zeros(myShape)
        return np.copy(result)
        

#Retourne une template avec les années chaque mois
    def templateAllYear(self):
        
        model=p.template
        model=model.copy()
        model.columns=model.columns.year
        return model.transpose()
    
#Retourne les frais de gestion par police
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
    
#Cette fonction retourne un vecteur avec les taux d'intérêt mensuel 
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
    
    def laspe(self):

        lapseRates=hyp.h.iloc[23:32,1:12]
        lapseRates.columns = lapseRates.iloc[0]
        lapseRates=lapseRates.drop(lapseRates.index[0])
        lapseRates=lapseRates.set_index('Year')
        
        mySize=list(hyp.un.shape)
        
        dur=p.durationIf()
        dur=dur[:mySize[0],:mySize[1],:mySize[2]]
        
        

        
        
        
        

#        ARRONDI(JOURS360([@[Date début]];'Cash flows par police'!$C$4)/30;0)
    


##############################ICI pour faire des tests sur la class##########################################################

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

#e=hyp.laspePerPolicy()











#A mettre en place:
#    - Taux--> e/o
#    - TauxPB--> e/o
#    - Sinistralité
#    - Lapse
#    - Reduction
#    - frais Gestion --> e/o
#    - frais gestion placement--> e/o
#    - Commissions
#    - Inflation
#    - Faire test pour les vecteurs (notament Rates)


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




