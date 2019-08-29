from iPortfolio import Portfolio
import pandas as pd

#Run Setting
#-	Quel run lancer 
#-	Quelle structure de produit
#Accumulation
#-	Défini les groupement de produits


# Export les inputs pour 1 run 
# Export le portfolio
# 
# for allRuns:
#     For allPorfolio:
#         Run all policies (avec un case statement sur la modalité qui appel toutes les fonctions de produits)
#    return les valeurs agrégée
#
#Faire les agrégations

resultat=pd.DataFrame()

for i in range(5):
    MonPortfolio=Portfolio(run=i)  
    resultat=resultat.append(MonPortfolio.PGG)



resultat.to_csv('Resultat_PGG.csv')

