import pandas as pd
import numpy as np
from MyPyliferisk.mortalitytables import EKM05i
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()


##############################################################################################################################
#Permet de recréer le fichier CSV du portefeuille en cas de modif de l'extraction
##############################################################################################################################  
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

#Attention enlever à la copie du test lorsque le développement sera fini
    return p.to_csv(r'Portefeuille\Portfolio.csv'), p.to_csv(r'Tests\Portfolio_Test.csv')


##############################################################################################################################
#Execution de l'extraction du portefeuille de polices requête SQL en CSV
##############################################################################################################################    

# portfolioExtractionToCSV()



##############################################################################################################################
#Inputs global permet de déterminer les date de calcul
##############################################################################################################################  
def dateInputs():
    return

dateCalcul='20181231'
dateFinCalcul='20521231' #A mon avis doit être remplacer par date expiration des polices (calculé dans projectionLengh())

##############################################################################################################################
#Permet d'ajouter deux colonnes avec la classPGG pour l'agrégation de la PGG (classPGG)
##############################################################################################################################    
def allocationDesClassPGG(p):
    p['zero']=0   
    dico=dict(zip(p['PMBMOD'],p['zero']))        
    #Les listes de numéro représente les mod a allouer chaque la catégorie
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

    
##############################################################################################################################
#Permet d'ajouter une colonne contenant le taux chargement d'ACQUISITION sur prime
############################################################################################################################## 
def premiumAquisitionLoading(p):
    
    #FU
    mask=(p['PMBMOD']==8)|(p['PMBMOD']==9)
    
    p.loc[mask,'aquisitionLoading']=0.2
    
    #AX
    mask=(p['PMBMOD']==70)

#Les frais d'aquisition sont erronés il faut changer pour 0.32   
    p.loc[mask,'aquisitionLoading']=0.25   
#    p.loc[mask,'aquisitionLoading']=0.32       

    #HO
    mask=(p['PMBMOD']==58)

#Les frais d'aquisition sont erronés il faut changer pour 0.25   
    p.loc[mask,'aquisitionLoading']=1  
#    p.loc[mask,'aquisitionLoading']=0.25

    
    # PRECI
    mask=(p['PMBMOD']==25)|(p['PMBMOD']==26)
    p.loc[mask,'aquisitionLoading']=0.25
    
    
    # Epargne retraite mod28 et mod29
    mask=(p['PMBMOD'].isin([28,29]))
    p.loc[mask,'aquisitionLoading']= (0.45 * np.minimum(p['POLDURC'], 20) /20)
    p.loc[mask,'aquisitionLoadingYear2']= 0
    p.loc[mask,'aquisitionLoadingYear3']= 0    

    # Epargne retraite mod32
    mask=(p['PMBMOD'].isin([32]))
    p.loc[mask,'aquisitionLoading']= (0.36 * np.minimum(p['POLDURC'], 20) /20)
    p.loc[mask,'aquisitionLoadingYear2']= (0.09 * np.minimum(p['POLDURC'], 20) /20)
    p.loc[mask,'aquisitionLoadingYear3']= 0    

    # Epargne retraite mod33
    mask=(p['PMBMOD'].isin([33]))
    p.loc[mask,'aquisitionLoading']= (0.445 * np.minimum(p['POLDURC'], 25) /25)
    p.loc[mask,'aquisitionLoadingYear2']= (0.395 * np.minimum(p['POLDURC'], 25) /25)
    p.loc[mask,'aquisitionLoadingYear3']= (0.395 * np.minimum(p['POLDURC'], 25) /25) 
    
    # Epargne retraite mod30 et mod31 et mod36
    mask=(p['PMBMOD'].isin([30,31,36]))
    p.loc[mask,'aquisitionLoading']=0    
    p.loc[mask,'aquisitionLoadingYear2']= 0
    p.loc[mask,'aquisitionLoadingYear3']= 0


    p['aquisitionLoading'].fillna(0,inplace=True)
    p['aquisitionLoadingYear2'].fillna(0,inplace=True)
    p['aquisitionLoadingYear3'].fillna(0,inplace=True)
    
##############################################################################################################################
#Permet d'ajouter une colonne contenant le taux chargement de GESTION sur prime
###################################################################################################################### 
    
def premiumGestionLoading(p):
    
    # Mod28 et Mod29
    mask=(p['PMBMOD'].isin([28,29,32]))
    p.loc[mask,'gestionLoading']=0.07
    
    # Mod30
    mask=(p['PMBMOD'].isin([30,31]))
    p.loc[mask,'gestionLoading']=0 
    
    # Mod33
    mask=(p['PMBMOD'].isin([33]))
    p.loc[mask,'gestionLoading']=0.055
    
    # Mod36
    mask=(p['PMBMOD'].isin([36]))
    p.loc[mask,'gestionLoading']=0.12
    
    # Mod11
    mask=(p['PMBMOD'].isin([11]))   
    p.loc[(p['Age1AtEntry'] < 53) & (mask), 'gestionLoading'] = 0.006
    p.loc[(p['Age1AtEntry'] >=53) & (p['Age1AtEntry'] < 70) & (mask), 'gestionLoading'] = 0.01
    p.loc[(p['Age1AtEntry'] >= 70) & (mask), 'gestionLoading'] = 0.021
   

##############################################################################################################################
#Permet d'ajouter une colonne contenant les frais de fractionnement
##############################################################################################################################
def fraisFractionnement(p):

    mask12=(p['PMBFRACT']==12)
    mask6=(p['PMBFRACT']==6)
    mask4=(p['PMBFRACT']==4)
    mask2=(p['PMBFRACT']==2) 
    
    maskAX=(p['PMBMOD']==70)
    
    p.loc[mask12 & maskAX,'fraisFract']=1.08
    p.loc[mask6 & maskAX,'fraisFract']=1.06
    p.loc[mask4 & maskAX,'fraisFract']=1.05
    p.loc[mask2 & maskAX,'fraisFract']=1.04
    
    
    maskPRECI=(p['PMBMOD']==25)|(p['PMBMOD']==26)
    
    p.loc[mask12 & maskPRECI,'fraisFract']=1.05
    p.loc[mask6 & maskPRECI,'fraisFract']=1.04
    p.loc[mask4 & maskPRECI,'fraisFract']=1.03
    p.loc[mask2 & maskPRECI,'fraisFract']=1.02
    
    
    p.loc[:,'fraisFract']=p.loc[:,'fraisFract'].fillna(1)

    
##############################################################################################################################
#Permet d'ajuster les polices réduite avec un fractionnement annuel 1 (Replication DCS)
##############################################################################################################################  
    
def adjustedFracAndPremium(p):
    
    mask = (p['PMBMOD'].isin([28,29,30,31,32,33,36,2,10,6,7])) & (p['PMBFRACT']==0)    
    p.loc[mask, 'PMBFRACT'] = 1
    mask= mask | (p['POLSIT']==4) 
    p.loc[mask,'POLPRTOT']=0
    
    
##############################################################################################################################
#Calcul de l'âge initial (l'âge du deuxième assuré qui n'existe pas est fixé à 999)
##############################################################################################################################    

def agesInitial(p):
    
    date1=pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d')
    
    date2=pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d')
    
    dateDebut= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d')
    
    dtNaiss1=np.where(date1.dt.month * 100 + date1.dt.day  > dateDebut.dt.month * 100 + dateDebut.dt.day , date1.dt.year  + 1, date1.dt.year)
    
    dtNaiss2=np.where(date2.dt.month * 100 + date2.dt.day  > dateDebut.dt.month * 100 + dateDebut.dt.day , date2.dt.year  + 1, date2.dt.year)
    
    p['Age1AtEntry']=dateDebut.dt.year-dtNaiss1
    p['Age2AtEntry']=dateDebut.dt.year-dtNaiss2
    p.loc[p.Age2AtEntry==0,'Age2AtEntry']=999
    
   
##############################################################################################################################
#Calcul de l'échéance des polices pour obtenir la durée des projections traité par modalité
##############################################################################################################################
def projectionLengh(p):

    p['residualTermM']=p['ProjectionMonths']
    p.loc[p['POLNBTETE']==1,'Age2AtEntry']=p.loc[p['POLNBTETE']==1,'Age1AtEntry']
    
    #Dertermination des âges limites
    ageMaxFU=65
    ageMaxAX=80
    ageMaxHO=75
    # ageMaxEP=55
  
#Traitement des mods 8 et 9
    mask=(p['PMBMOD']==8)|(p['PMBMOD']==9)
    
    p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].max(axis=1)
    p.loc[mask,'residualTermM']=((ageMaxFU-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']
 
    #Nous pensons que cette variante est plus correct car dans le mod 9 la police continue jusqu'à 65 ans du plus jeune assuré
    #Il faut ajouté le code commenté pour prendre en compte le changement et supprimé le mod neuf du mask du mod 8 
 
    # mask=(p['PMBMOD']==9)    

    # p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].min(axis=1)
    # p.loc[mask,'residualTermM']=((ageMaxFU-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']


#Traitement du mod 70
    mask=(p['PMBMOD']==70)
    
    p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].max(axis=1)
    p.loc[mask,'residualTermM']=((ageMaxAX-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']


 # Traitement du mod 58
    mask=(p['PMBMOD']==58)
    p.loc[mask,'residualTermM']=((ageMaxHO-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']

 # # Traitement du mod 29
 #    mask=(p['PMBMOD']==29)
 #    p.loc[mask,'residualTermM']=((ageMaxEP-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']    
    
    #Replacer 999 pour les deuxièmes assurés des polices à une tête
    p.loc[p['POLNBTETE']==1,'Age2AtEntry']=999


##############################################################################################################################
#Correction des ages et du résidual terme pour Axiprotect et Preciso (Réplication Prophet) A supprimer pour corriger
##############################################################################################################################

def adjustAgesAndTerm(p):

#    p=porN
    
    
#Traitement des mod 70,25,26
    mask=(p['PMBMOD']==70)|(p['PMBMOD']==25)|(p['PMBMOD']==26)
    
    date1=pd.to_datetime(p.loc[mask,'CLIDTNAISS'])
    
    date2=pd.to_datetime(p.loc[mask,'CLIDTNAISS2'])
    
    dateDebut=pd.to_datetime(p.loc[mask,'POLDTDEB'])
         
    age1=(((12*(dateDebut.dt.year-date1.dt.year)+dateDebut.dt.month-date1.dt.month+(dateDebut.dt.day/100)-(date1.dt.day/100))/12)+0.5).astype(int)
    age2=(((12*(dateDebut.dt.year-date2.dt.year)+dateDebut.dt.month-date2.dt.month+(dateDebut.dt.day/100)-(date2.dt.day/100))/12)+0.5).astype(int)

    p.loc[mask,'Age1AtEntry']=age1
    p.loc[mask,'Age2AtEntry']=age2
 
    mask1=(mask) & (p['POLNBTETE']==1)    
    p.loc[mask1,'residualTermM']= (65-p.loc[mask1,'Age1AtEntry'])*12-p.loc[mask1,'DurationIfInitial']

    mask2=(mask) & (p['POLNBTETE']==2) 
    
    p.loc[mask2,'residualTermM']=p.loc[mask2,['Age2AtEntry','Age1AtEntry']].max(axis=1)
    p.loc[mask2,'residualTermM']=((70-p.loc[mask2,'residualTermM'])*12)-p.loc[mask2,'DurationIfInitial']
 
    decalage=pd.ExcelFile(path  + '/Hypotheses/Decalage.xlsx').parse("Feuil1")
    
    decalage=decalage['DECALAGE'].to_dict()

    p.loc[mask2,'ageDiff']=abs(p.loc[mask2,'Age1AtEntry']-p.loc[mask2,'Age2AtEntry'])
    p.loc[mask1,'ageDiff']=p.loc[mask1,'ageDiff'].fillna(0)

    
    p['ageDecalage']=p['ageDiff'].map(decalage)

    p.loc[mask2,'Age1AtEntry']=np.minimum(p.loc[mask2,'Age1AtEntry'],p.loc[mask2,'Age2AtEntry'])+ p.loc[mask2,'ageDecalage']
    
    p.loc[mask,'Age2AtEntry']=999
    
    p.loc[p['residualTermM']<0,'residualTermM']=0


##############################################################################################################################
#Correction des ages pour HOSPITALIS/SERENITE . A supprimer pour corriger
########################################################################################################################
       
    mask=(p['PMBMOD']==58)|(p['PMBMOD']==11)
    
    date1=pd.to_datetime(p.loc[mask,'CLIDTNAISS'])
       
    moisnaiss1 = date1.dt.month*1
    
    dateDebut=pd.to_datetime(p.loc[mask,'POLDTDEB'])
    
#  Condition présente dans les DCS
    mask2 =(np.absolute(date1.dt.month - dateDebut.dt.month) == 6)
    
    mask3 = (dateDebut.dt.day < date1.dt.day)
    
    moisnaiss1[mask3 & mask2] =  moisnaiss1+1
    
    age1=(((12*(dateDebut.dt.year-date1.dt.year)+dateDebut.dt.month-moisnaiss1)/12)+0.5).astype(int)

    p.loc[mask,'Age1AtEntry']=age1
    
    mask=(p['PMBMOD']==58)
    p.loc[mask,'residualTermM']=((75-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']

# On force l'age 2 à 999 car les DCS ne prennent pas en compte la 2ème tête
    p.loc[mask,'Age2AtEntry']=999
    
   
    
    
##############################################################################################################################
#Correction des ages et residual pour TEMPORAIRE. A supprimer pour corriger
########################################################################################################################

            
    mask=(p['PMBMOD'].isin([28,29,30,31,32,33,36]))
    
    date1=pd.to_datetime(p.loc[mask,'CLIDTNAISS'])
    
    date2=pd.to_datetime(p.loc[mask,'CLIDTNAISS2'])
    
    dateDebut=pd.to_datetime(p.loc[mask,'POLDTDEB'])
         
    age1=(((12*(dateDebut.dt.year-date1.dt.year)+dateDebut.dt.month-date1.dt.month+(dateDebut.dt.day/100)-(date1.dt.day/100))/12)+0.5).astype(int)
    age2=(((12*(dateDebut.dt.year-date2.dt.year)+dateDebut.dt.month-date2.dt.month+(dateDebut.dt.day/100)-(date2.dt.day/100))/12)+0.5).astype(int)

    p.loc[mask,'Age1AtEntry']=age1
    p.loc[mask,'Age2AtEntry']=age2
 
    mask1=(mask) & (p['POLNBTETE']==1)    
    p.loc[mask1,'residualTermM']= p.loc[mask1,'POLDURC']*12-p.loc[mask1,'DurationIfInitial']

    mask2=(mask) & (p['POLNBTETE']==2) 
    
    p.loc[mask2,'residualTermM']= p.loc[mask2,'POLDURC']*12-p.loc[mask2,'DurationIfInitial']
 
    decalage=pd.ExcelFile(path  + '/Hypotheses/Decalage.xlsx').parse("Feuil1")
    
    decalage=decalage['DECALAGE'].to_dict()

    p.loc[mask2,'ageDiff']=abs(p.loc[mask2,'Age1AtEntry']-p.loc[mask2,'Age2AtEntry'])
    p.loc[mask1,'ageDiff']=p.loc[mask1,'ageDiff'].fillna(0)
 
    p['ageDecalage']=p['ageDiff'].map(decalage)

    p.loc[mask2,'Age1AtEntry']=np.minimum(p.loc[mask2,'Age1AtEntry'],p.loc[mask2,'Age2AtEntry'])+ p.loc[mask2,'ageDecalage']
    
    p.loc[mask,'Age2AtEntry']=999
    
    p.loc[p['residualTermM']<0,'residualTermM']=0
            
        
       
    
##############################################################################################################################
#Permet de formater la dataframe du portefeuille des polices avant d'entrer dans la classe Hypo
#traitement des anomalies et mise en forme des colonnes
##############################################################################################################################

def portfolioPreProcessing(p):

#Traitement des anomalies dans les données

    #Certaines dates d'échéances tombe un jour qui n'existe pas
    p.loc[p['PMBPOL'].isin([1602101,609403,2161101,2162601,297004]), 'POLDTEXP'] = '20190228'
    
    #Lorsqu'il y a de l'agravation dans les Funérailles la prime initial est prise
    p.loc[p['PMBPOL'].isin([602802,2130001,2141101,2149401,2165602,2190101,2216301,2265503,2349803,2547906]), 'POLPRTOT']=240
    
    #Une date de naissance a été corrigée rétroactivement, nous replacons la date de naissance présente à la clôture    
    p.loc[p['PMBPOL'].isin([60602]), 'CLIDTNAISS2'] = '19551009'

    p.loc[p['PMBPOL'].isin([786502]), 'CLIDTNAISS'] = '19611028'
    
    #Lorsque la police a une tête l'age du deuxième assuré est 0 donc il né à la date début de la police (ensuite 999 ans)
    p.loc[p.POLNBTETE==1, 'CLIDTNAISS2'] = p.loc[p.POLNBTETE==1, 'POLDTDEB']
    
    #Une police mod 70 est par construction déjà échue le premier mois elle ne rentre pas dans prophet
    p=p.drop(p.loc[p['PMBPOL'].isin([1054602])].index)
    

    agesInitial(p)
    
#Formatage des colonnes et création des colonnes utiles    

    p['DateCalcul']=pd.to_datetime(dateCalcul)
    p['DateFinCalcul']=pd.to_datetime(dateFinCalcul)
    
    #Formatage des date en format date
    p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
    p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date
    p['CLIDTNAISS']= pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.date   
    p['CLIDTNAISS2']= pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.date
    
    #Nombre de mois de projection selon la date fin de calcul hardcodé qui est voué à disparaitre 
    p['ProjectionMonths']=((pd.to_datetime(p['DateFinCalcul'])-pd.to_datetime(p['DateCalcul'])) \
     /np.timedelta64(1,'M')).apply(np.ceil)
    
##On pense que la différence en mois est plus correct que le calcul des DCS pour les duration IF
#    p['DurationIfInitial']=((pd.to_datetime(p['DateCalcul'])-pd.to_datetime(p['POLDTDEB']))/np.timedelta64(1,'M')).apply(np.around)
    p['DurationIfInitial']=(pd.to_datetime(p['DateCalcul']).dt.year - pd.to_datetime(p['POLDTDEB']).dt.year)*12 \
    + pd.to_datetime(p['DateCalcul']).dt.month - pd.to_datetime(p['POLDTDEB']).dt.month + 1  
    
    

    #Nombre de mois de projection selon la date de fin des polices
    projectionLengh(p)
    
    #Création des collones pour l'agragation de la PGG
    allocationDesClassPGG(p)
    
    #Création des PM servant de base pour le calcul de la PGG
    p['PMbasePGG']=p['PMBPRVMAT']+p['PMBPBEN']+p['PMBREC']+p['PMBRECCPL']
    
    #Traitement des ages et policy terme selon Prophet pour mod70 (nous pensons que cela est erroné)
    adjustAgesAndTerm(p)
        
    # Ajout de la colonne contenant les chargements d'acquisition
    premiumAquisitionLoading(p)
    
    # Ajout de la colonne contenant les chargements de gestion
    premiumGestionLoading(p)
    
    #Ajout d'une colonne contenant les frais de fractionnement
    fraisFractionnement(p)
    
    # Ajustement des fractionnements pour des polices avec frac = 0 (réduites)
    adjustedFracAndPremium(p)
    
    

    return p




##############################################################################################################################
#CHARGEMENT DES FICHIERS INPUTS
#- Hypothèses N et N-1
#- Portefeuille N et N-1
#- les runs possible
#- La table de mortalité d'expérience
##############################################################################################################################
def chargementINPUTS():
    return 

hypN=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypotheses")
hypN_1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypotheses")

porN=pd.read_csv(path+'/Portefeuille\Portfolio.csv')
porN=portfolioPreProcessing(porN)

porN_1=pd.read_csv(path+'/Portefeuille\Portfolio.csv')
porN_1=portfolioPreProcessing(porN_1)

allRuns=[0,1,2,3,4,5]

tableExperience=EKM05i
   

##############################################################################################################################
#Création de la class Hypothèse
##############################################################################################################################

class Hypo:
    
#    __slot__=('un','vide','zero','run','shape')

    def __init__(self,hy=hypN,hy1=hypN_1,po=porN, po1=porN_1,Run=allRuns, \
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        
        if PortfolioNew:
            self.tout=po 
            self.p=po
        else:
            self.tout=po1
            self.p=po1
        
        self.h0=hy
        self.h1=hy1
        
        self.runs=Run
        self.shape=list(self.one().shape)
        self.SinistralityNew=SinistralityNew
        self.LapseNew=LapseNew
        self.CostNew=CostNew
        self.RateNew=RateNew

#        self.securityMarginMarge=1+self.h.iloc[53,2]
#        self.securityMarginBio=1+self.h.iloc[54,2]

 
##############################################################################################################################
###################################DEBUT DES METHODES DE DIMENSSIONEMENT######################################################
##############################################################################################################################

#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[]
    def mod(self,mods):
       sp=self.tout.loc[self.tout['PMBMOD'].isin(mods)]
       self.update(sp)
       return sp
   
#Permet de retourner un mask pour une liste de modalité
    def mask(self,mods):
       myMask=(self.p['PMBMOD'].isin(mods)).to_numpy()[:,np.newaxis,np.newaxis]*self.one()
       return myMask.astype(bool)
   
#Permet de retourner un sous-portefeuille sélectionné de la liste de mods=[] et le nombre de tête
    def modHead(self,mods,nbrhead):
       sp=self.tout.loc[(self.tout['PMBMOD'].isin(mods)) & (self.tout['POLNBTETE'].isin([nbrhead])) ]
       self.update(sp)
       return sp
   
#Permet de retourner un sous-portefeuille sélectionné de la liste de num=[]
    def ids(self,num):
        sp=self.tout.loc[self.tout['PMBPOL'].isin(num)]
        self.update(sp)
        return sp
#Permet de retourner un sous-portefeuille sélectionné de la liste de gr=[]
    def groupe(self,gr):
        sp=self.tout.loc[self.tout['ClassPGG'].isin(gr)]
        self.update(sp)
        return sp

#Permet de mettre à jour le portefeuille avec le sous-portefeuille de traitement
    def update(self,subPortfolio):
        self.p=subPortfolio
        self.shape=list(self.one().shape)
        self.runs=self.runs
        
#Permet de créer un vecteur  rempli de 1 pour la taille de portefeuille et la durée de projection  
    def one(self):
        nbrPolices=int(len(self.p))
        nbrPeriodes= int(self.p['residualTermM'].max()+1)
        nbrRuns=int(len(self.runs))
        return np.copy(np.ones([nbrPolices,nbrPeriodes,nbrRuns]))

#Permet de créer un vecteur rempli de 0 pour la taille de portefeuille et la durée de projection  
    def zero(self):             
        return np.copy(np.zeros_like(self.one()))
    
#Permet de créer un vecteur rempli VIDE pour la taille de portefeuille et la durée de projection  
    def vide(self):             
        return np.copy(np.empty_like(self.one()))

# Retourne une template formaté pour tous les runs avec des 0  
    def templateAllrun(self):             
        myShape=self.shape
        myShape[2]=int(len(allRuns))
        result=np.zeros(myShape)
        return np.copy(result)
    
# Retourne une template formaté pour tous les runs de 1   
    def oneAllrun(self):             
        myShape=self.shape
        myShape[2]=int(len(allRuns))
        result=np.ones(myShape)
        return np.copy(result)


# Retourne une template avec les années chaque mois
    def templateAllYear(self):
        model=pd.date_range(start=self.p['DateCalcul'].min(), periods=int(self.p['residualTermM'].max()+1), freq='M')
        model=pd.DataFrame(model).set_index(0).transpose()       
        model=model.copy()
        model.columns=model.columns.year
        return model.transpose()

#Retourne le set d'hypothèse en fonction d'un boolean Si isNew=True alors hypothèse N sinon N-1   
    def hypoSet(self,isNew):      
        if isNew:
            h=self.h0
        else:
            h=self.h1
        return h
        

##############################################################################################################################
###################################DEBUT DES METHODES DES HYPOTHESES##########################################################
##############################################################################################################################
   
# Retourne les frais de gestion par police (coût par police)
    def fraisGestion(self):
        
        h=self.hypoSet(self.CostNew)
                
        adminCost=self.templateAllrun()
        
        adminCost[:,:,:4]=h.iloc[49,3]
        adminCost[:,:,4]=h.iloc[49,4]
        adminCost[:,:,5]=h.iloc[49,5]
        #Dimensionner pour les runs en appel    
        adminCost=adminCost[:,:,self.runs] 
        
        return adminCost/12
    
# Retourne les frais de gestion des placements qui s'applique aux PM    
    def fraisGestionPlacement(self):
        
        h=self.hypoSet(self.CostNew)
        
        investCost=self.templateAllrun()
        
        investCost[:,:,:4]=h.iloc[50,3]
        investCost[:,:,4]=h.iloc[50,4]
        investCost[:,:,5]=h.iloc[50,5]
        #Dimensionner pour les runs en appel    
        investCost=investCost[:,:,self.runs]
        
        return investCost/1200

#Retourne une template qui s'applique pour tous les taux de sinistralité   
    def templateSinistrality(self,a):

        h=self.hypoSet(self.SinistralityNew) 
        
        bestEstimate=h.iloc[a,3]
        bePlusMarge=h.iloc[a,4]
        bioEtFrais=h.iloc[a,5]

        sin=self.templateAllrun()
        
        sin[:,:,:4]=bestEstimate
        sin[:,:,4]=bePlusMarge
        sin[:,:,5]=bioEtFrais
        #Dimensionner pour les runs en appel    
        sin=sin[:,:,self.runs]
        
        return sin

#Retourne les taux de sinistralité IPT (incapacité permanente et total)
    def ipt(self):
        return self.templateSinistrality(14)

#Retourne les taux de sinistralité du décès accidentel
    def dcAccident(self):
        return self.templateSinistrality(15)

#Retourne les taux de sinistralité de l'exonération du paiement des primes
    def exo(self):
        return self.templateSinistrality(16)
    
#Retourne les taux de sinistralité de l' ITT (incapacité temporaire total)
    def itt(self):
        return self.templateSinistrality(17)

#Retourne les taux de sinistralité de l'hospitalisation
    def hospi(self):
        return self.templateSinistrality(18)

#Retourne les taux de mortalité d'expérience
    def dc(self):
        return self.templateSinistrality(19)
    
#Retourne les taux de sinistralité des frais de visite
    def fraisVisite(self):
        return self.templateSinistrality(20)
    
#Retourne les taux d'intérêt mensualisé pour l'actualisation financière
    def rate(self):

        h=self.hypoSet(self.RateNew)
        
        rates=self.templateAllrun()       
        model=self.templateAllYear()
        model=model.iloc[:self.shape[1]]
        
        allrates=h.iloc[2:6,1:39].transpose()
        
        allrates=pd.merge(model,allrates, left_on=0,right_on=2,how='left')
        allrates=allrates.fillna(0)
        allrates=allrates.iloc[:,2:].to_numpy()
        
        #Conversion en taux mensuel
        allMensualrates=(1+allrates)**(1/12)-1
        allMensualrates=allMensualrates[np.newaxis,:,:]
        
        #Quel run pour quel courbe        
        runBE=[0,5,2,3]
        runRL=1
        runMG=4
        #Remplir la template pour chaque runs        
        rates[:,:,runBE]=allMensualrates[:,:,0,np.newaxis]
        rates[:,:,runMG]=allMensualrates[:,:,1]
        rates[:,:,runRL]=allMensualrates[:,:,2]
        #Dimensionner pour les runs en appel    
        rates=rates[:,:,self.runs]
        
        return rates

#Retourne les taux d'intérêt mensualisé pour la participation aux excédant
    def pbRate(self):

        h=self.hypoSet(self.RateNew)
        
        fixratePB=h.iloc[45,2]/100
        
        rate=self.rate()
        
        ratesPB=((1+rate)**12-1)-fixratePB
        
        return ratesPB

#Retourne les taux de rachat selon le fractionnement. Les taux apparaissent uniquement le mois avant un paiement de prime
    def lapse(self):

        h=self.hypoSet(self.LapseNew)
        
        lapseSensiMoins=h.iloc[56,2]
        lapseSensiPlus=h.iloc[57,2]       
        cl=self.p['ClassPGGinit']
        
        lapseRates=h.iloc[23:32,1:12]
        lapseRates.columns = lapseRates.iloc[0]
        lapseRates=lapseRates.drop(lapseRates.index[0])
        lapseRates=lapseRates.set_index('Year').transpose()
        lapseRates=lapseRates[cl].transpose().to_numpy()
        lapseRates=lapseRates[:,:,np.newaxis,np.newaxis]

        dur=self.durationIf()
        dur=dur[:,:,0][:,:,np.newaxis]*self.oneAllrun()
        

        condlist = [dur<=12,dur<=24,dur<=36,dur<=48,dur<=60, 
                    dur<=72,dur<=84,dur<=96,dur<=108, 
                    dur>108]
        choicelist = [lapseRates[:,0,:],lapseRates[:,1,:],lapseRates[:,2,:], 
                      lapseRates[:,3,:],lapseRates[:,4,:],lapseRates[:,5,:], 
                      lapseRates[:,6,:],lapseRates[:,7,:],lapseRates[:,8,:], 
                      lapseRates[:,9,:] ]
        mylapse=np.select(condlist, choicelist)

        
        mylapse[:,:,[3,4]]=mylapse[:,:,[3,4]]*lapseSensiMoins
        mylapse[:,:,2]=mylapse[:,:,2]*lapseSensiPlus
       
        #Dimensionner pour les runs et le portefeuille en appel    
        mylapse=mylapse[:,:,self.runs]
        
        #Prise en compte du taux fractionnel et de la mise en place avant un paiement
        frac=self.frac()
        
        #Fractionnement à 0 sont remplacer par 1
        frac[frac==0]=12
        mylapse=1-(1-mylapse)**(1/frac)
        
        mylapse= self.isLapse()*mylapse
        
        return mylapse

#Retourne les taux de réduction annuel
    def reduction(self):

        h=self.hypoSet(self.LapseNew)  
        
        # A vérifier si même sensibilité que rachat 
        lapseSensiMoins=h.iloc[56,2]
        lapseSensiPlus=h.iloc[57,2] 
        
        cl=self.p['ClassPGGinit']
        reductionRates=h.iloc[34:43,1:12]
        reductionRates.columns = reductionRates.iloc[0]
        reductionRates=reductionRates.drop(reductionRates.index[0])
        reductionRates=reductionRates.set_index('Year').transpose()
        reductionRates=reductionRates[cl].transpose().to_numpy()
        reductionRates=reductionRates[:,:,np.newaxis,np.newaxis]

        dur=self.durationIf()
        dur=dur[:,:,0][:,:,np.newaxis]*self.oneAllrun()       
      

        condlist = [dur<=12,dur<=24,dur<=36,dur<=48,dur<=60, 
                    dur<=72,dur<=84,dur<=96,dur<=108, 
                    dur>108]
        choicelist = [reductionRates[:,0,:],reductionRates[:,1,:],reductionRates[:,2,:], 
                      reductionRates[:,3,:],reductionRates[:,4,:],reductionRates[:,5,:], 
                      reductionRates[:,6,:],reductionRates[:,7,:],reductionRates[:,8,:], 
                      reductionRates[:,9,:] ]
        myReduction=np.select(condlist, choicelist)

        
        myReduction[:,:,[3,5]]=myReduction[:,:,[3,5]]*lapseSensiMoins
        myReduction[:,:,2]=myReduction[:,:,2]*lapseSensiPlus
       
              
        
        #Dimensionner pour les runs et le portefeuille en appel    
        myReduction=myReduction[:,:,self.runs]
        
        
        # JO mensualisé selon le fractionnement le taux de reduction annuel/ JO ajout également de self.frac() qui était à 12 avant
        myReduction = 1-(1-myReduction)**(1/self.frac())
        
        
        #  Reduction rate au temps 0 = 0
        myReduction[:,0,:] = 0
        
        # JO ajout de isLapse car la reduction n'apparait uniquement le mois d'avant le paiement de la prime
        return myReduction*self.isLapse()

#Retourne les taux de commissions incluant les commissions de gestion     
    def commissions(self):

        h=self.hypoSet(self.CostNew)
        cl=self.p['PMBMOD']
        
        commissionsRates=h.iloc[61:85,1:7]
        commissionsRates.columns = commissionsRates.iloc[0]
        commissionsRates=commissionsRates.drop(commissionsRates.index[0])
        commissionsRates=commissionsRates.set_index('Modalité').transpose()
        commissionsRates=commissionsRates[cl].transpose().to_numpy()
        commissionsRates=commissionsRates[:,:,np.newaxis,np.newaxis]
        
        dur=self.durationIf()      
        dur=dur[:,:,0][:,:,np.newaxis]*self.oneAllrun()
        polTermM=self.polTermM()

        condlist = [dur<=12,dur<=24,dur<=36,(dur>36) & (dur<polTermM),(dur>36) & (dur>=polTermM)]
        
        choicelist = [commissionsRates[:,0,:],commissionsRates[:,1,:],commissionsRates[:,2,:],commissionsRates[:,4,:],0]
        
        myCommissions=np.select(condlist, choicelist)
        
        #Dimensionner pour les runs et le portefeuille en appel
        myCommissions=myCommissions[:,:,self.runs]
        
        return myCommissions

#Retourne le taux mensuel d'inflation dimensionné pour les runs et polices
    def inflation(self):
        
        h=self.hypoSet(self.CostNew)
        
        inflationRate=h.iloc[55,2]
        
        inflationRate=inflationRate+self.one()
        
        increment=np.arange(0,self.shape[1])[np.newaxis,:,np.newaxis]
            
        inflationMensuel= inflationRate**(increment/12)
              
        return inflationMensuel
    
##############################################################################################################################
###################################DEBUT DES METHODES DU CALCUL DES PRODUITS#################################################
##############################################################################################################################

#Retourne un vecteur du nombre de mois que la police est en vigeur qui s'incrémente de 1 par mois
    def durationIf(self):
        
        durationInitial=self.p['DurationIfInitial'].to_numpy()
        
        durationInitial=durationInitial[:,np.newaxis,np.newaxis]
        
        increment=np.arange(0,self.shape[1],1)
        increment=increment[np.newaxis,:,np.newaxis]
            
        durIf=self.one()     
        durIf=durIf*durationInitial        
        durIf=durIf+increment
        
        return durIf

#Retourne un vecteur contenant la durée de la police en mois
    def polTermM(self):
        return (self.p['residualTermM']+self.p['DurationIfInitial']).to_numpy()[:,np.newaxis,np.newaxis]*self.one()

#Retourne le fractionnement constant de chaque polices
    def frac(self):
        
        fract = self.one() * self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        return fract


#Retourn un 1 lorsqu'il y a un lapse possible, soit le mois qui précède le paiement d'une prime   
    def isLapse(self):
        lapse = self.zero()
        check1 = (self.frac() * (self.durationIf() + 12) /12)
        check2 = np.floor((self.frac() * (self.durationIf() + 12) /12))

        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [lapse[:,:,:]==0, lapse[:,:,:] ==1 ]
        
        myLapse=np.select(condlist, choicelist)
        
        # Le premier mois il n'y a pas de payement car la prime est payé en début de mois et les date de calcul sont en fin de mois
        myLapse[:,0,:] = 0
        
        return myLapse

#Retourn un 1 lorsqu'il y a un payement de prime
    def isPremPay(self):
        
        payement = self.zero()
        check1 = (self.frac() * (self.durationIf() + 11) /12)
        check2 = np.floor((self.frac() * (self.durationIf() + 11) /12))

        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [payement[:,:,:]==0, payement[:,:,:] ==1 ]
        
        myPayement=np.select(condlist, choicelist)
        
        # Le premier mois il n'y a pas de payement car la prime est payé en début de mois et les date de calcul sont en fin de mois
        myPayement[:,0,:] = 0
        
        return myPayement

#Renvoi un vecteur des années de projection pour par rapport aux anniversaires des polices partant de 0
    def projectionYear(self):
        
        durif = self.p['DurationIfInitial'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()-1
        durif = np.remainder(durif, 12)
        increment = np.cumsum(self.one(), axis = 1) -1 + durif
        
        return np.floor(increment/12)
    
  
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
def testerHypo():
    return 0

#myHypo=Hypo(Run=[0,5])
# myHypo=Hypo()

# myHypo.mod([8,9,70,58])
# p = myHypo.ids([10105])
#myHypo.groupe(['MI3.5'])


###Les méthodes de la class

#za=myHypo.tout
# zb=myHypo.p
#zc=myHypo.runs
#zd=myHypo.shape
#ze=myHypo.one()
#zf=myHypo.zero()
#zg=myHypo.vide()
# zh=myHypo.templateAllYear()
#zi=myHypo.fraisGestion()
#zj=myHypo.fraisGestionPlacement()
#zk=myHypo.rate()
#zl=myHypo.pbRate()
#zm=myHypo.lapse()
#zn=myHypo.ipt()
#zo=myHypo.dcAccident()
#zp=myHypo.exo()
#zq=myHypo.itt()
#zr=myHypo.hospi()
#zs=myHypo.dc()
#zt=myHypo.fraisVisite()
#zu=myHypo.reduction()
#zv=myHypo.commissions()
#zw=myHypo.inflation()

# qq =myHypo.polTermM()
print("Class Hypo--- %s sec" %'%.2f'%  (time.time() - start_time))

###Visualiser un vecteur np en réduisant une dimension
#data=m
#a=pd.DataFrame(data[:,:,1])


#a=porN.loc[porN['PMBMOD']==70]
