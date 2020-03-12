from Portefeuille import Portfolio
from Parametres import allRuns
from Produits import FU,AX,HO,PR
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
##############################################################################################################################
class RUNPGG():

    def __init__(self):
        self

#Retourne une df avec la PGG pour chaque sous-portefeuille
    def pggParSousPortefeuille(self,runNumber=allRuns,\
                               isPortfolioNew=True, isSinistralityNew=True,isLapseNew=True,isCostNew=True,isRateNew=True):

#Ajout de funéraille           
        fu=FU(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        fu=fu.PGG()
 
#Ajout d'axiprotect      
        ax=AX(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        ax=ax.PGG()

#Ajout d'hospitalis      
        ho=HO(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        ho=ho.PGG()

#Ajout des PRECISO     
        pr=PR(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        pr=pr.PGG()

#Agrégation des sous-portefeuille dans une DF       
        pggTotal=pd.DataFrame(fu)
        pggTotal=pggTotal.append([ax,ho,pr])
        
        
        return pggTotal

#Retourne la PGG total avec les hypothèses N   
    def pggTotal(self):
        
        spPGG=self.pggParSousPortefeuille()
        
        spPGG=sum(spPGG['PGG'])
        
        return spPGG

#Retourne la PGG par sous-portefeuille contenant la mise à jour de chaque hypothèse une par une    
    def deltaAnalysisSousPortefeuille(self):
        
        initial=self.pggParSousPortefeuille(runNumber=allRuns,isPortfolioNew=False, isSinistralityNew=False,\
                                            isLapseNew=False,isCostNew=False,isRateNew=False)
        initial['Etape']='initial'

        portfolio=self.pggParSousPortefeuille(runNumber=allRuns,isPortfolioNew=True, isSinistralityNew=False,\
                                            isLapseNew=False,isCostNew=False,isRateNew=False)
        portfolio['Etape']='portfolio'
        
        sinistrality=self.pggParSousPortefeuille(runNumber=allRuns,isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=False,isCostNew=False,isRateNew=False)
        sinistrality['Etape']='sinistrality'
        
        lapse=self.pggParSousPortefeuille(runNumber=allRuns,isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=True,isCostNew=False,isRateNew=False)
        lapse['Etape']='lapse'
        
        cost=self.pggParSousPortefeuille(runNumber=allRuns,isPortfolioNew=True, isSinistralityNew=True,\
                                            isLapseNew=True,isCostNew=False,isRateNew=False)
        cost['Etape']='cost'       

        rate=self.pggParSousPortefeuille(runNumber=allRuns,isPortfolioNew=True, isSinistralityNew=True,\
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

a=run.pggParSousPortefeuille()
# b=run.pggTotal()
# c=run.deltaAnalysisSousPortefeuille()
# d=run.deltaAnalysisPGG()



print("Class RUN--- %s sec" %'%.2f'%  (time.time() - start_time))