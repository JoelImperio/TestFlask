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


p['DateCalcul']=pd.to_datetime(dateCalcul)
p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date
p['ProjectionMonths']=((pd.to_datetime(p['POLDTEXP'])-pd.to_datetime(p['DateCalcul']))/np.timedelta64(1,'M')).apply(np.ceil)+1




#Création de la class Portefeuille

class portfolio:
    
    
    def __init__(self):
        self.tout=p        
        self.p=p
        self.un=self.one()
        self.zero=self.zeros()
        self.vide=self.vides()
        self.template= self.templateProjection()


    
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def mod(self,mods):
       sp=self.p.loc[self.p['PMBMOD'].isin(mods)]
       self.update(sp)
       return sp
   
#Permet de retourner un sous-portefeuille sélectionné de la liste de num=[]
    def ids(self,num):
        sp=self.p.loc[self.p['PMBPOL'].isin(num)]
        self.update(sp)
        return sp

#Permet de mettre à jour le portefeuille avec le sous-portefeuille de traitement
    def update(self,subPortfolio):
        self.p=subPortfolio
        self.un=self.one()
        self.zero=self.zeros()
        self.vide=self.vides()
        self.template= self.templateProjection()
        
#Permet de créer un vecteur  rempli de 1 pour la taille de portefeuille et la durée de projection  
    def one(self):
        nbrPolices=int(len(self.p))
        nbrPeriodes= int(self.p['ProjectionMonths'].max())     
        return np.ones([nbrPolices,nbrPeriodes])

#Permet de créer un vecteur rempli de 0 pour la taille de portefeuille et la durée de projection  
    def zeros(self):             
        return np.zeros_like(self.un)
    
#Permet de créer un vecteur rempli VIDE pour la taille de portefeuille et la durée de projection  
    def vides(self):             
        return np.empty_like(self.un)

#Permet de retourner une DF indexé par le temps de projection permet ensuite d'append les resultats de chaque police  
    def templateProjection(self): 
        myTemplate=pd.date_range(start=self.p['DateCalcul'].min(), end=self.p['POLDTEXP'].max(), freq='M')
        myTemplate=pd.DataFrame(myTemplate).set_index(0).transpose()            
        return myTemplate


policies=portfolio()
a=policies.template
b=policies.ids([301,2501])
c=policies.template
        




