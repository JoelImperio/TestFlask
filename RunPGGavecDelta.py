from iPortfolio import Portfolio
import pandas as pd


resultat=pd.DataFrame()

for i in range(5):
    MonPortfolio=Portfolio(run=i, LapseNew=False, Sinistrality=False)  
    resultat=resultat.append(MonPortfolio.PGG)
    
    MonPortfolio2=Portfolio(run=i, Sinistrality=False)  
    resultat=resultat.append(MonPortfolio2.PGG)
    
    MonPortfolio3=Portfolio(run=i)  
    resultat=resultat.append(MonPortfolio3.PGG)

resultat.to_csv('Resultat_PGG.csv')