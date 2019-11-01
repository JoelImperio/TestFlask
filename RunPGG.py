from Portefeuille import Portfolio
from Parametres import allRuns
from Produits import FU
import numpy as np
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

    def pggParSousPortefeuille(self,runNumber=allRuns,\
                               isPortfolioNew=True, isSinistralityNew=True,isLapseNew=True,isCostNew=True,isRateNew=True):
            
        fu=FU(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        fu=fu.PGG()
        
        mi=FU(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        mi=mi.PGG()
        
        pggTotal=pd.DataFrame(fu)
        pggTotal=pggTotal.append(mi)
        
        
        return pggTotal
    
    def pggTotal(self):
        
        spPGG=self.pggParSousPortefeuille()
        
        spPGG=sum(spPGG['PGG'])
        
        return spPGG
    
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
    
    def deltaAnalysisPGG(self):
        
        spDelta=self.deltaAnalysisSousPortefeuille()
        
        totalDelta=spDelta.groupby(['Etape'], sort=False).sum()
        
        totalDelta['Delta']=totalDelta.diff().fillna(0)
        
        return totalDelta
        
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################       
 
#run=RUNPGG()

#a=run.pggParSousPortefeuille()
#b=run.pggTotal()
#c=run.deltaAnalysisSousPortefeuille()
#d=run.deltaAnalysisPGG()



print("Class RUN--- %s sec" %'%.2f'%  (time.time() - start_time))