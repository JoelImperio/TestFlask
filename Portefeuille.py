
import pandas as pd
import numpy as np
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

#Permet de recréer le fichier CSV du portefeuille en cas de modif de l'extraction
def portfolioExtractionToCSV():
    import pyodbc
      
    #Paramètres de connection
    cnxn = pyodbc.connect(
        driver='{iSeries Access ODBC Driver}',
        system='10.254.25.1',
        uid='liviaplus',
        pwd='liviaplus')  
    #Extraction du portefeuille des polices   
    PortfolioQRY=open(r'Portefeuille\QRY.txt').read()
    p=pd.read_sql(PortfolioQRY, cnxn)
    #Copy l'extraction dans un CSV
    p.to_csv(r'Portefeuille\Portfolio.csv')

#Inputs global
dateCalcul='20181231'
dateFinCalcul='20521231' #A mon avis doit être remplacer par date expiration des polices

#Extraction du portefeuille de polices
#portfolioExtractionToCSV()

p=pd.read_csv(path+'/Portefeuille\Portfolio.csv')

#Permet de crée une colonne avec la classPGG
def allocationClassPGG():
    p['zero']=0   
    dico=dict(zip(p['PMBMOD'],p['zero']))        
    #Les listes de numéro représente les mod a allouer dans la catégorie
    for i in [2,10,6,7]:
        dico[i]='MI'       
    for i in [1,11]:
        dico[i]='VE'
    for i in [3,4]:
        dico[i]='TE'
    for i in [25,26]:
        dico[i]='PR'
    for i in [8,9,12]:
        dico[i]='FU'       
    for i in [28,29,30,31,32,33,36]:      
        dico[i]='EP'  
    for i in [58]:
        dico[i]='HO'
    for i in [70]:
        dico[i]='AX'
    #Creation des classes PGG génériques
    p['ClassPGGinit'] = p['PMBMOD'].map(dico)
    #Creation des classesPGG avec txInt pour les EP et MI
    p['ClassPGG']=p['ClassPGGinit']
    p.loc[p['ClassPGGinit'].isin(['EP','MI']),'ClassPGG']= \
    p.loc[p['ClassPGGinit'].isin(['EP','MI']),'ClassPGGinit'].map(str)+ \
    p.loc[p['ClassPGGinit'].isin(['EP','MI']),'PMBTXINT'].map(str)

#Permet de formater la dataframe des polices avant d'entrer dans la classe
def portfolioPreProcessing(p):

#Traitement des anomalies dans les données

    #Certaines dates d'échéances tombe un jour qui n'existe pas
    p.loc[p['PMBPOL'].isin([1602101,609403,2161101,2162601,297004]), 'POLDTEXP'] = '20190228'

#Formatage des colonnes et création des colonnes utiles    

    p['DateCalcul']=pd.to_datetime(dateCalcul)

##On pense que la solution en commentaire est meilleure mais ptophet effectue l'autre
#    p['DateFinCalcul']=p['POLDTEXP']
    p['DateFinCalcul']=pd.to_datetime(dateFinCalcul)
    
    p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
    p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date
    p['ProjectionMonths']=((pd.to_datetime(p['DateFinCalcul'])-pd.to_datetime(p['DateCalcul']))/np.timedelta64(1,'M')).apply(np.ceil)+1
    p['DurationIfInitial']=((pd.to_datetime(p['DateCalcul'])-pd.to_datetime(p['POLDTDEB']))/np.timedelta64(1,'M')).apply(np.ceil)
    allocationClassPGG()


    return p

p=portfolioPreProcessing(p)

#Création de la class Portefeuille

class Portfolio:
    

    
    def __init__(self,po=p,runs=[0,1,2,3,4,5], \
                 LapseNew=True,RateNew=True,SinistralityNew=True,CommissionNew=True,CostNew=True):
        self.tout=po    
        self.p=po
        self.runs=runs
        self.un=self.one()
        self.zero=self.zeros()
        self.vide=self.vides()
        self.template= self.templateProjection()
        self.shape=list(self.un.shape)


#        from Parametres import Hypo
#        self.lapse=Hypo(MyShape=self.shape,Run=runs,New=LapseNew).lapse()    
#        self.waver=Hypo(MyShape=self.shape,Run=runs,New=LapseNew)
#        self.rate=Hypo(MyShape=self.shape,Run=runs,New=RateNew)
#        self.ratePb=Hypo(MyShape=self.shape,Run=runs,New=RateNew)
#        self.sinistrality=Hypo(MyShape=self.shape,Run=runs,New=SinistralityNew)
#        self.commissions=Hypo(MyShape=self.shape,Run=runs,New=CommissionNew)
#        self.fixeCost=Hypo(MyShape=self.shape,Run=runs,New=CostNew)
#        self.investCost=Hypo(MyShape=self.shape,Run=runs,New=CostNew)


    
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
        self.shape=list(self.un.shape)
        self.runs=self.runs
        
#Permet de créer un vecteur  rempli de 1 pour la taille de portefeuille et la durée de projection  
    def one(self):
        nbrPolices=int(len(self.p))
        nbrPeriodes= int(self.p['ProjectionMonths'].max())
        nbrRuns=int(len(self.runs))
        return np.ones([nbrPolices,nbrPeriodes,nbrRuns])

#Permet de créer un vecteur rempli de 0 pour la taille de portefeuille et la durée de projection  
    def zeros(self):             
        return np.zeros_like(self.un)
    
#Permet de créer un vecteur rempli VIDE pour la taille de portefeuille et la durée de projection  
    def vides(self):             
        return np.empty_like(self.un)

#Permet de retourner une DF indexé par le temps de projection permet ensuite d'append les resultats de chaque police  
    def templateProjection(self): 
        myTemplate=pd.date_range(start=self.p['DateCalcul'].min(), end=self.p['DateFinCalcul'].max(), freq='M')
        myTemplate=pd.DataFrame(myTemplate).set_index(0).transpose()            
        return myTemplate

#####DEBUT DES VARIABLES DE CALCUL DES PROJECTIONS#################################################

    def durationIf(self):
        
        durationInitial=self.p['DurationIfInitial'].to_numpy()
        
        durationInitial=durationInitial[:,np.newaxis,np.newaxis]
        
        increment=np.arange(0,policies.shape[1],1)
        increment=increment[np.newaxis,:,np.newaxis]
            
        durIf=self.un
        
        durIf=durIf*durationInitial
        
        durIf=durIf+increment
        
        return durIf
        
        








#####ICI pour faire des tests sur la class##########################################################

policies=Portfolio()
c=policies.ids([2401101])
a=policies.durationIf()

#b=policies.shape
#c=policies.ids([301,2501])
#d=policies.un
#e=policies.shape
#f=policies.rate()


    




