import pandas as pd
#import pyodbc


#Paramètres de connection
#cnxn = pyodbc.connect(
#    driver='{iSeries Access ODBC Driver}',
#    system='10.254.25.1',
#    uid='liviaplus',
#    pwd='liviaplus')


#Extraction du portefeuille des polices

#PortfolioQRY=open(r'Portefeuille\Portfolio.csv').read()
#vporpolpm=pd.read_sql(PortfolioQRY, cnxn)
#vporpolpm.to_csv(r'Portefeuille\Portfolio.csv')

#Extraction du portefeuille de polices

vporpolpm=pd.read_csv(r'Portefeuille\Portfolio.csv')


#Formatage des colonnes et création des colonnes utiles

p=vporpolpm
#[['PMBMOD','PMBPOL']]


#Création de la class Portefeuille

class portfolio:
    
    tout=p
    
    def __init(self):
        self        
    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def mod(mods):
       return p.loc[p['PMBMOD'].isin(mods)]
   
#Permet de retourner un sous-portefeuille sélectionné de la liste de num=[]
    def ids(num):
       return p.loc[p['PMBPOL'].isin(num)]

        



