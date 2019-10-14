
import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

#Permet de recréer le fichier CSV du portefeuille en cas de modif de l'extraction
def portfolioExtractionToCSV():
    import pyodbc
      
    #Paramètres de connection
    cnxn = pyodbc.connect(
        driver='{iSeries Access ODBC Driver}',
        system='10.254.5.1',
        uid='liviaplus',
        pwd='liviaplus')  
    #Extraction du portefeuille des polices   
    PortfolioQRY=open(r'Portefeuille\QRY.txt').read()
    p=pd.read_sql(PortfolioQRY, cnxn)
    #Copy l'extraction dans un CSV

#Attention enlever à la copie du test
    return p.to_csv(r'Portefeuille\Portfolio.csv'), p.to_csv(r'Tests\Portfolio_Test.csv')

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

    pd.options.display.float_format = '{:.2f}'.format
    
    #Certaines dates d'échéances tombe un jour qui n'existe pas
    p.loc[p['PMBPOL'].isin([1602101,609403,2161101,2162601,297004]), 'POLDTEXP'] = '20190228'
    
    #Lorsque la police a une tête l'age du deuxième assuré est 0 donc il né à la date début de la police (ensuite 999 ans)
    p.loc[p.POLNBTETE==1, 'CLIDTNAISS2'] = p.loc[p.POLNBTETE==1, 'POLDTDEB']

#Formatage des colonnes et création des colonnes utiles    

    p['DateCalcul']=pd.to_datetime(dateCalcul)
    

##On pense que la solution en commentaire est meilleure mais ptophet effectue l'autre
#    p['DateFinCalcul']=p['POLDTEXP']
    p['DateFinCalcul']=pd.to_datetime(dateFinCalcul)
    
    p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
    p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date
#    p['CLIDTNAISS']= pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.date
    

     
#    p['CLIDTNAISS2']= pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.date
   
    
    p['ProjectionMonths']=((pd.to_datetime(p['DateFinCalcul'])-pd.to_datetime(p['DateCalcul']))/np.timedelta64(1,'M')).apply(np.ceil)
    
# JO Problème polices 872401 : prophet duration if = 41 , python = 42. 
# CODE DCS : DURATIONIF_M = (YEAR(EXTRACT_DATE)- annee_deb) * 12 + month(extract_date) - MOIS_DEB +1 

    p['DurationIfInitial']=(pd.to_datetime(p['DateCalcul']).dt.year - pd.to_datetime(p['POLDTDEB']).dt.year)*12 + pd.to_datetime(p['DateCalcul']).dt.month - pd.to_datetime(p['POLDTDEB']).dt.month + 1
    
#    p['DurationIfInitial']=((pd.to_datetime(p['DateCalcul'])-pd.to_datetime(p['POLDTDEB']))/np.timedelta64(1,'M')).apply(np.ceil)
    allocationClassPGG()

# JO serait clairement plus correct mais dans les DCS le code est : AGE_AT_ENTRY = Annee_deb - Annee_naiss1
#    p['Age1AtEntry']=((pd.to_datetime(p['POLDTDEB'])-pd.to_datetime(p['CLIDTNAISS']))/np.timedelta64(1,'Y')).apply(np.ceil)
#    p['Age2AtEntry']=((pd.to_datetime(p['POLDTDEB'])-pd.to_datetime(p['CLIDTNAISS2']))/np.timedelta64(1,'Y')).apply(np.ceil)
    
    
# JO il faut ajouter le "subterfuge" de PhM pour obtenir le même age
    
    moisnaiss1 = pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.month
    journaiss1 = pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.day
    annenaiss1 = pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.year
    moisdeb = pd.to_datetime(p['POLDTDEB']).dt.month
    jourdeb = pd.to_datetime(p['POLDTDEB']).dt.day
    
    moisnaiss2 = pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.month
    journaiss2 = pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.day
    annenaiss2 = pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.year
    
    naiss1 = np.where(moisnaiss1 * 100 + journaiss1  >= moisdeb * 100 + jourdeb , annenaiss1  + 1, annenaiss1)
    naiss2 = np.where(moisnaiss2 * 100 + journaiss2 >= moisdeb * 100 + jourdeb ,annenaiss2 + 1, annenaiss2)
    
    p['Age1AtEntry']=pd.to_datetime(p['POLDTDEB']).dt.year-naiss1
    p['Age2AtEntry']=pd.to_datetime(p['POLDTDEB']).dt.year-naiss2
    

    



    
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
#Permet de retourner un sous-portefeuille sélectionné de la liste de gr=[]
    def groupe(self,gr):
        sp=self.p.loc[self.p['ClassPGG'].isin(gr)]
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
    
# Test pour pouvoir calculé de manière recusrive
    def oneplusone(self):
        nbrPolices=int(len(self.p))
        nbrPeriodes= int(self.p['ProjectionMonths'].max())
        nbrRuns=int(len(self.runs))
        return np.ones([nbrPolices,nbrPeriodes+1,nbrRuns])
    
    
    

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

#Retourne un vecteur du nombre de mois que la police est en vigeur

    def durationIf(self):
        
        durationInitial=self.p['DurationIfInitial'].to_numpy()
        
        durationInitial=durationInitial[:,np.newaxis,np.newaxis]
        
        increment=np.arange(0,self.shape[1],1)
        increment=increment[np.newaxis,:,np.newaxis]
            
        durIf=self.un       
        durIf=durIf*durationInitial        
        durIf=durIf+increment
        return durIf
    
#Retourne le vecteur des ages pour l'assuré 1 ou 2 (defaut assuré 1) 
# JO Problème age était pendant 12 mois le même depuis t=0, mais cela va dépendre de durif. ajout de durif dans le calcul
# JO problème car le changement d'âge avait lieu avec un décalage d'un mois comparé a prophet (donc j'ai enlevé un mois dans le durif et rajouter 0.0001 = problème d'arrondi à régler)
    def age(self,ass=1):

        ageInitial=self.p['Age{}AtEntry'.format(ass)].to_numpy()        
        ageInitial=ageInitial[:,np.newaxis,np.newaxis]
        
        increment = np.floor(np.float64((self.durationIf()/12) - (1/12)+0.00001))
        
        age=self.zero       
        age=age+ageInitial         
        age=np.where(age<=0,age+999,age+increment)
        return np.floor(age)

#Retourne un vecteur des qx dimensionné correctement pour une table de mortalité, 
# une expérience (100 = 100% de la table) et pour l'assuré 1 ou 2  

    def qx(self,table=EKM05i, exp=100, ass=1):
         
        mt=MortalityTable(nt=table, perc=exp)
        
        aQx=pd.DataFrame(mt.qx).to_numpy()
        
        myAge=(self.age(ass)).astype(int) 
        myAge=np.where(myAge>mt.w,mt.w-1,myAge)
        return np.take(aQx,myAge)   



    def qxmensuel(self):
# JO ligne de code qui évite un code d'erreur   
        qxmens = np.array(-1, dtype=np.complex)
    
# JO Calcul qx mensuel du 1er assuré
        qxmens1 = 1-(1-self.qx(exp=41.73,ass=1))**(1/12)
        qxmens1[:,0,:] = 0
        
# JO Calcul qx mensuel du 2ème assuré
        qxmens2 = 1-(1-self.qx(exp=41.73,ass=2))**(1/12)
        qxmens2[:,0,:] = 0
        
# JO calcul du qx total si il y a 2 têtes et prend le qx du 1er assuré s'il y a une tête
        condlist = [self.nbassure() ==1, self.nbassure() ==2]
        choicelist = [qxmens1 , qxmens1 + qxmens2 - qxmens1*qxmens2 ]
        qxmens=np.select(condlist, choicelist)
        return qxmens


# JO changement pour avoir des fractionnement formaté en 3D
    def fractionnement(self):
        
        fract = self.un
        fract = fract * self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        return fract


# JO Ajout vecteur de 1 ou 0 si il y a paiement de prime ou non
    def mypayement(self):
        
        payement = self.zeros()

        check1 = (self.fractionnement() * (self.durationIf() + 11) /12)
        check2 = np.floor((self.fractionnement() * (self.durationIf() + 11) /12))
        
        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [payement[:,:,:]==0, payement[:,:,:] ==1 ]
        
        myPayement=np.select(condlist, choicelist)
# JO on ne reçoit pas de paiement à t=0 POURQUOI ??? Question à se poser sur quand est-ce qu'on reçoit la prime (début ou fin de mois)
        myPayement[:,0,:] = 0
        
        return myPayement


    def nbassure(self):
        
        nombreass = self.p['POLNBTETE'].to_numpy()[:,np.newaxis,np.newaxis] * self.un
        return nombreass
    
# JO Création d'un vecteur d'inflation A CHANGER VALEUR EN DUR !!!
    def inflation(self):
        
        inflation = 1.0125**(np.arange(np.size(self,1))[np.newaxis,:,np.newaxis]/12)
        return inflation
    

    
    

    
#####ICI pour faire des tests sur la class##########################################################

policies=Portfolio()

#Les fonctions de la class Portfolio()
#a=policies.tout
#b=policies.p
#c=policies.runs
#d=policies.shape
#e=policies.mod([8,9])

#policies.ids([911101])

#policies.ids([872401])
#policies.ids([2501801])
#policies.ids([75203])
#policies.ids([893801])
#policies.ids([317401])
#g=policies.groupe(['MI3.5'])
#h=policies.un
#i=policies.zero
#j=policies.vide
#k=policies.template
#l=policies.durationIf()
#m=policies.age(2)
#n=policies.qx(table=EKM05i, exp=100,ass=1)


