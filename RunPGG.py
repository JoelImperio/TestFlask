from Parametres import allRuns
from Produits import FU,AX,HO,PR,EP,VE,MI
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
##############################################################################################################################
class RUNPGG():

    def __init__(self):
        self.allSP=[FU,AX,HO,PR,EP,VE,MI]

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

#Ajout des épargnes     
        ep=EP(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        ep=ep.PGG()
        
#Ajout des vie entières    
        ve=VE(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        ve=ve.PGG()

#Ajout des mixtes  
        mi=MI(run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)    
        mi=mi.PGG()

#Agrégation des sous-portefeuille dans une DF       
        pggTotal=pd.DataFrame(fu)
        pggTotal=pggTotal.append([ax,ho,pr,ep,ve,mi])
        
        
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

#Retourne une df avec la PGG pour chaque sous-portefeuille
    def pggParSousPortefeuille2(self,runNumber=allRuns,\
                               isPortfolioNew=True, isSinistralityNew=True,isLapseNew=True,isCostNew=True,isRateNew=True):
        
        pggTotal=pd.DataFrame()
        for i in range(len(self.allSP)):
            
            sp=self.allSP[i](run=runNumber,PortfolioNew=isPortfolioNew, SinistralityNew=isSinistralityNew,\
              LapseNew=isLapseNew,CostNew=isCostNew,RateNew=isRateNew)
            sp=sp.PGG()
            
            pggTotal=pggTotal.append(sp)

                
        return pggTotal

        
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################       
 
# run=RUNPGG()

a=run.pggParSousPortefeuille2()
# b=run.pggTotal()
# c=run.deltaAnalysisSousPortefeuille()
# d=run.deltaAnalysisPGG()

#Tester de récupérer toutes les méthodes et storer tout les résultats
# a=FU()
# b = dir(a)
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