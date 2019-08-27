import pandas as pd
import pyodbc


#Paramètres de connection
cnxn = pyodbc.connect(
    driver='{iSeries Access ODBC Driver}',
    system='10.254.25.1',
    uid='liviaplus',
    pwd='liviaplus')


#Extraction du portefeuille des polices

#PortfolioQRY=open(r'Portfolio\Portfolio.csv').read()
#p=pd.read_sql(PortfolioQRY, cnxn)
#p.to_csv(r'Portfolio\Portfolio.csv')

#Extraction du portefeuille de polices

p=pd.read_csv(r'Portfolio\Portfolio.csv')



#Formatage des colonnes et création des colonnes utiles



#Création de la class Portefeuille

class portfolio:
    
    tout=p
    
    def __init(self):
        self
    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mod=[]
    def mods(mod):
       return p.loc[p['PMBMOD'].isin(mod)]
   
#Permet de retourner un sous-portefeuille sélectionné de la liste de num=[]
    def ids(num):
       return p.loc[p['PMBPOL'].isin(num)]

        



