from Parametres import Inputs
from Produits import FU,AX,HO,PR,TE,VE,EP,MI
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

myInputs=Inputs()

##############################################################################################################################
##############################################################################################################################
class RUNPGG():

    def __init__(self):
        
        self.allSP=[FU,AX,HO,PR,TE,VE,EP,MI]

#Retourne une df avec la PGG pour chaque sous-portefeuille
    def pggParSousPortefeuille(self,inp=myInputs,\
                               isPortfolioNew=True, isSinistralityNew=True,isLapseNew=True,isCostNew=True,isRateNew=True):
        
        pggTotal=pd.DataFrame()
        for i in range(len(self.allSP)):
            
            sp=self.allSP[i](inputs=inp,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)
            sp=sp.PGG()
            
            pggTotal=pggTotal.append(sp)
           
        return pggTotal


#Retourne la PGG total avec les hypothèses N   
    def pggTotal(self):
        
        spPGG=self.pggParSousPortefeuille()
        
        spPGG=sum(spPGG['PGG'])
        
        return spPGG

#Retourne la PGG par sous-portefeuille contenant la mise à jour de chaque hypothèse une par une    
    def deltaAnalysisSousPortefeuille(self):
        
        initial=self.pggParSousPortefeuille(isPortfolioNew=False, isSinistralityNew=False,\
                                            isLapseNew=False,isCostNew=False,isRateNew=False)
        initial['Etape']='initial'

        portfolio=self.pggParSousPortefeuille(isPortfolioNew=True, isSinistralityNew=False,\
                                            isLapseNew=False,isCostNew=False,isRateNew=False)
        portfolio['Etape']='portfolio'
        
        sinistrality=self.pggParSousPortefeuille(isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=False,isCostNew=False,isRateNew=False)
        sinistrality['Etape']='sinistrality'
        
        lapse=self.pggParSousPortefeuille(isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=True,isCostNew=False,isRateNew=False)
        lapse['Etape']='lapse'
        
        cost=self.pggParSousPortefeuille(isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=True,isCostNew=False,isRateNew=False)
        cost['Etape']='cost'       

        rate=self.pggParSousPortefeuille(isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=True,isCostNew=False,isRateNew=True)
        rate['Etape']='rate'    
        
        deltaAnalysis=initial.append([portfolio,sinistrality,lapse,cost,rate])
        
        return deltaAnalysis

#Retourne la PGG total avec l'analyse du delta de chaque mise à jour d'hypothèse    
    def deltaAnalysisPGG(self):
        
        spDelta=self.deltaAnalysisSousPortefeuille()
        
        totalDelta=spDelta.groupby(['Etape'], sort=False).sum()
        
        totalDelta['Delta']=totalDelta.diff().fillna(0)
        
        return totalDelta



        
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################       
 
run=RUNPGG()

# a=run.pggParSousPortefeuille()
# b=run.pggTotal()
# c=run.deltaAnalysisSousPortefeuille()
# d=run.deltaAnalysisPGG()

#Tester de récupérer toutes les méthodes et storer tout les résultats
# a=FU()
# b = dir(a)
# c=pd.DataFrame( a.__class__.__dict__.items())
# y=pd.DataFrame(columns=['Method','Resultat'])

# for i in range(len(b)):

#     try:
#         x=getattr(a,b[i])()
#     except:
#         x=getattr(a,b[i])
#     else:
#         pass
    
#     y.loc[i]=[b[i],x]


# y.to_excel(path+'/zRW/VariablesRapport.xlsx')




print("Class RUN--- %s sec" %'%.2f'%  (time.time() - start_time))