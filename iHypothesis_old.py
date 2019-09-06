import pandas as pd
import numpy as np
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
 

#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")


#Création de la class Portefeuille

class Hypo:
    
    __slot__=('un','vide','zero','run','shape', 'p')

    def __init__(self,hy=h,hy1=h1,MyShape=[],Run=[0,1,2,3,4,5], New=True, MyPortfolio=0):
        self.run=Run
        self.shape=MyShape
        self.p=MyPortfolio
        self.un=np.ones(shape)
        self.vide=np.empty_like(self.un)
        self.zero=np.zeros_like(self.un)
        if New:
            self.h=hy
        else:
            self.h=hy1
        self.securityMarginMarge=1+self.h.iloc[47,2]
        self.securityMarginBio=1+self.h.iloc[48,2]

        
#Cette méthode permet de retourner un array selon la liste de conditons choiceForEachRun='[run0,..,run5]'        
    def ifsRun(self,choiceForEachRun):

#       Les Variables appelées avec les choiceForEachRun
        
        #variables des coûts
        adminCost=self.h.iloc[43,3]*(self.un)
        investCost=self.h.iloc[44,3]*(self.un)
        interestRate=self.h.iloc[2:6,1:38].transpose()
        
        #Variables des taux
        rates=self.getRates()
        
        #Variables taux PB
        ratePB=self.h.iloc[39,2]/100
        
        #Variable de la méthode
        result=self.zero
        listeDesRuns=self.run
        uno=self.un
        for i in range(len(listeDesRuns)):
            z=listeDesRuns[i]*uno
            condlist = [z[:,:,i]==0,z[:,:,i]==1,z[:,:,i]==2,z[:,:,i]==3,z[:,:,i]==4,z[:,:,i]==5]
            result[:,:,i]=np.select(condlist, eval(choiceForEachRun))
        return np.copy(result)
    
    def getRates(self):
        
        allrates=self.h.iloc[2:6,1:38].transpose()
        model=self.model_year()
        allrates=pd.merge(model,allrates, left_on=0,right_on=2,how='left')
        allrates=allrates.fillna(0).transpose().to_numpy()

        rateBE=(allrates[3,:])[np.newaxis,:,np.newaxis]
        rateMarge=(allrates[4,:])[np.newaxis,:,np.newaxis]
        rateRL=(allrates[5,:])[np.newaxis,:,np.newaxis]

        rates=self.zero
        if rates.shape[1]>rateBE.shape[1]:
            rates[:,:rateBE.shape[1],[0,2,3,5]]=(1+rateBE)**(1/12)-1
            rates[:,:rateRL.shape[1],[1]]=(1+rateRL)**(1/12)-1
            rates[:,:rateMarge.shape[1],[4]]=(1+rateMarge)**(1/12)-1
        else:
            rates[:,:,[0,2,3,5]]=(1+rateBE[:,:rates.shape[1],:])**(1/12)-1
            rates[:,:,[1]]=(1+rateRL[:,:rates.shape[1],:])**(1/12)-1
            rates[:,:,[4]]=(1+rateMarge[:,:rates.shape[1],:])**(1/12)-1
        return rates
    
    def model_year(self):
        
        model=self.p.template
        model=model.copy()
        model.columns=model.columns.year
        return model.transpose()

    def fraisGestion(self):

        choiceForEachRun='[adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i],adminCost[:,:,i],\
        adminCost[:,:,i]*self.securityMarginMarge,adminCost[:,:,i]*self.securityMarginBio]'    
        
        return self.ifsRun(choiceForEachRun)
    
    
    def fraisGestionPlacement(self):

        choiceForEachRun='[investCost[:,:,i],investCost[:,:,i],investCost[:,:,i],investCost[:,:,i], \
        investCost[:,:,i]*self.securityMarginMarge,investCost[:,:,i]*self.securityMarginBio]'    
        
        return self.ifsRun(choiceForEachRun)


    def rate(self):
        choiceForEachRun='[rates[:,:,0],rates[:,:,1],rates[:,:,2],\
        rates[:,:,3],rates[:,:,4],rates[:,:,5]]'    
        
        return self.ifsRun(choiceForEachRun)
    
    def pbRate(self):
        choiceForEachRun='[rates[:,:,0]-ratePB,rates[:,:,1]-ratePB,rates[:,:,2]-ratePB,\
        rates[:,:,3]-ratePB,rates[:,:,4]-ratePB,rates[:,:,5]-ratePB]'    
    
        return self.ifsRun(choiceForEachRun)

    


##############################ICI pour faire des tests sur la class##########################################################
from iPortfolio import Portfolio
myRun=[1,5]
#myRun=[0,1,2,3,4,5]
policies=Portfolio(runs=myRun)
#policies.mod([8,9])
shape=policies.shape

hyp1=Hypo(MyShape=shape, Run=myRun, MyPortfolio=policies)


a=hyp1.rate()
#b=hyp1.pbRate()
#c=hyp1.getRates()


#c.columns=c.columns.year
#c=c.transpose()
#allrates=h.iloc[2:6,1:38].transpose()
#allrates=pd.merge(c,allrates, left_on=0,right_on=2)
#allrates=allrates.transpose()
#
#e=(d.loc[3,:])[np.newaxis,:,np.newaxis]

#rates=(np.zeros((3392,200,6))).copy()
#allrates=h.iloc[2:6,1:38].transpose()
#rateBE=(np.repeat(allrates.iloc[1:,1].to_numpy(),12))[np.newaxis,:,np.newaxis]
#rateRL=(np.repeat(allrates.iloc[1:,3].to_numpy(),12))[np.newaxis,:,np.newaxis]
#rateMarge=(np.repeat(allrates.iloc[1:,2].to_numpy(),12))[np.newaxis,:,np.newaxis]
#rates[:,:rateBE.shape[1],[0,2,3,5]]=rateBE
#rates[:,:rateRL.shape[1],[1]]=rateRL
#rates[:,:rateMarge.shape[1],[4]]=rateMarge
#rates[:,:,[0,2,3,5]]=rateBE[:,:rates.shape[1],:]
#rates[:,:,[1]]=rateRL[:,:rates.shape[1],:]
#rates[:,:,[4]]=rateMarge[:,:rates.shape[1],:]








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




