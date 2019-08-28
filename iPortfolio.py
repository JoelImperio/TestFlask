import pandas as pd
import numpy as np
import time
#import pyodbc
#
#
##Paramètres de connection
#cnxn = pyodbc.connect(
#    driver='{iSeries Access ODBC Driver}',
#    system='10.254.25.1',
#    uid='liviaplus',
#    pwd='liviaplus')
#
#
##Extraction du portefeuille des polices
#
#PortfolioQRY=open(r'Portefeuille\QRY.txt').read()
#p=pd.read_sql(PortfolioQRY, cnxn)
#p.to_csv(r'Portefeuille\Portfolio.csv')

#Inputs global
dateCalcul='20181231'

#Extraction du portefeuille de polices

p=pd.read_csv(r'Portefeuille\Portfolio.csv')

#Traitement des anomalies dans les données

#Certaines dates d'échéances tombe un jour qui n'existe pas
p.loc[p['PMBPOL'].isin([1602101,609403,2161101,2162601,297004]), 'POLDTEXP'] = '20190228'

#Formatage des colonnes et création des colonnes utiles


#p['NewVariable']=

p['DateCalcul']=pd.to_datetime(dateCalcul)
p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date

p['ProjectionMonths']=((pd.to_datetime(p['POLDTEXP'])-pd.to_datetime(p['DateCalcul']))/np.timedelta64(1,'M')).apply(np.ceil)


aa=pd.date_range(start=p['DateCalcul'].min(), end=p['POLDTEXP'].max(), freq='M')
aa=pd.DataFrame(aa).set_index(0).transpose()




#Création de la class Portefeuille

class portfolio:
    
    
    def __init__(self):
        self.tout=p        
        self.p=p

    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def mod(self,mods):
       return self.p.loc[self.p['PMBMOD'].isin(mods)]
   
#Permet de retourner un sous-portefeuille sélectionné de la liste de num=[]
    def ids(self,num):
       return self.p.loc[self.p['PMBPOL'].isin(num)]

#Permet de mettre à jour le portefeuille avec le sous-portefeuille de traitement
    def update(self,subPortfolio):
        self.p=subPortfolio
    
    def one(self,subPortfolio):
        self.update(subPortfolio)
        nbrPolices=len(self.p)
        nbrPeriodes= self.p
        

        

policies=portfolio()
a=policies.ids([301,2501])
b=policies.mod([8,9])
c=policies.p
d=policies.update(b)
e=policies.p
