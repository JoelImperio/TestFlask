import pandas as pd
import numpy as np
from MyPyliferisk.mortalitytables import EKM05i
import time
import sys
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()


        
# =============================================================================
#  Création de la classe Inputs
# =============================================================================

class Inputs:

    def __init__(self, use='PGG'):

        self.usedFor=use  
        
        #A définir
        self.moisJourCalcul='1231'     
        self.myRuns=[0,1,2,3,4,5]
        self.allRuns=[0,1,2,3,4,5]        
        self.tableExperience=EKM05i
        
        #Chargement des fichiers
        
        self.hy=pd.ExcelFile(path  + '/Inputs/'+self.usedFor+'/HypoN.xls').parse("Hypotheses")
        self.hy1=pd.ExcelFile(path  + '/Inputs/'+self.usedFor+'/HypoN-1.xls').parse("Hypotheses")

        porN=pd.read_csv(path+'/Inputs/'+self.usedFor+'/PortfolioN.csv')
        porN_1=pd.read_csv(path+'/Inputs/'+self.usedFor+'/PortfolioN-1.csv')
            
        self.decalage=pd.ExcelFile(path  + '/Inputs/Decalage.xlsx').parse("Feuil1")
        self.loading=pd.ExcelFile(path  + '/Inputs/Loading.xlsx').parse("Loading")
        
        #!! A supprimer fichier correction des classes pour les mixtes
        self.newClass=pd.read_excel(path+'/Inputs/CorrespondanceProduit.xlsx',sheet_name='MIXTES')
        
      
        self.po=self.portfolioPreProcessing(porN)
        self.po1=self.portfolioPreProcessing(porN_1)
              
    def clean(self):             
        return [self.hy,self.hy1,self.po,self.po1,self.myRuns]
    
    #Extraction du portefeuille des polices à partir du fichier qryN ou qryN-1
    def portfolioExtractionToCSV(self):
        import pyodbc      
        #Paramètres de connection
        cnxn = pyodbc.connect(
            driver='{iSeries Access ODBC Driver}',
            system='10.254.5.1',
            uid='liviaplus',
            pwd='liviaplus')  
        #Extraction du portefeuille N   
        n='N'
        PortfolioQRY=open(path+'/Inputs/'+self.usedFor+'/qry'+n+'.txt').read()
        p=pd.read_sql(PortfolioQRY, cnxn)
        p.to_csv(path+'/Inputs/'+self.usedFor+'/Portfolio'+n+'.csv') 

        #Extraction du portefeuille N-1 
        n1='N-1'
        PortfolioQRYn1=open(path+'/Inputs/'+self.usedFor+'/qry'+n1+'.txt').read()
        p1=pd.read_sql(PortfolioQRYn1, cnxn)
        p1.to_csv(path+'/Inputs/'+self.usedFor+'/Portfolio'+n1+'.csv')    
        
        return p,p1 

    def aSupprimer_DataError(self,p):

    #Traitement des anomalies dans les données    
        #Certaines dates d'échéances tombe un jour qui n'existe pas
        p.loc[p['PMBPOL'].isin([1602101,609403,2161101,2162601,297004]), 'POLDTEXP'] = '20190228'
        
        #Lorsqu'il y a de l'agravation dans les Funérailles la prime initial est prise
        p.loc[p['PMBPOL'].isin([602802,2130001,2141101,2149401,2165602,2190101,2216301,2265503,2349803,2547906]), 'POLPRTOT']=240
        
        #Une date de naissance a été corrigée rétroactivement, nous replacons la date de naissance présente à la clôture    
        p.loc[p['PMBPOL'].isin([60602]), 'CLIDTNAISS2'] = '19551009' 
        p.loc[p['PMBPOL'].isin([786502]), 'CLIDTNAISS'] = '19611028'     
        p.loc[p['PMBPOL'].isin([3101]), 'CLIDTNAISS'] = '19700910'
        p.loc[p['PMBPOL'].isin([783401]), 'CLIDTNAISS'] = '19730718'
            
        #Une police mod 70 est par construction déjà échue le premier mois elle ne rentre pas dans prophet
        p=p.drop(p.loc[p['PMBPOL'].isin([1054602])].index)
        
        #Une police Hospitalis a un taux d'indexation sur la prime à 3%
        p.loc[p['PMBPOL'].isin([1637202]), 'POLINDEX'] = 0
        # Une police axiprotect a un taux d'indexation sur la prime à 1%, on force à 0
        p.loc[p['PMBPOL'].isin([2357801]), 'POLINDEX'] = 0

        # Prophet considère que toutes les TEMPORAIRES mod3 et 4 possèdent une table GKM95
        mask3_4 = p['PMBMOD'].isin([3,4])
        p.loc[mask3_4, 'POLTBMORT'] = 'GKM1995'
        
        return p


    # Les allocations dans les classes PGG ne correspondait pas aux taux technique pour les mixtes
    def aSupprimer_ReAllocClassPGG_Mixte(self,p):
        
        
        
        newClasse=pd.Series(self.newClass['ClassePGG'].values, index=self.newClass['ID'] ).to_dict()
        
        p['ClassPGG2']=p['PMBPOL'].map(newClasse)
        
        p.loc[p['ClassPGG2'].isnull()==False,'ClassPGG']= p.loc[p['ClassPGG2'].isnull()==False,'ClassPGG2']
        
        return p

    #Réplication des DCS mais on pense que le calcul de la différence de mois est plus correct
    def aSupprimer_FixationDeLaDurationInitiale(self,p):
        
        p['DurationIfInitial']=(pd.to_datetime(p['DateCalcul']).dt.year - pd.to_datetime(p['POLDTDEB']).dt.year)*12 \
        + pd.to_datetime(p['DateCalcul']).dt.month - pd.to_datetime(p['POLDTDEB']).dt.month + 1 
        return p
    
    #Réplication des residual terme
    def aSupprimer_CorrResidualTermM(self,p):
    
        #mod 9
        #la police continue jusqu'à 65 ans du plus jeune assuré alors que c'est l'inverse actuellement
        ageMaxFU=65
        mask=(p['PMBMOD']==9)   
        p.loc[(mask) & (p['POLNBTETE']==1),'Age2AtEntry']=p.loc[(mask)& (p['POLNBTETE']==1),'Age1AtEntry']
        p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].max(axis=1)
        p.loc[mask,'residualTermM']=((ageMaxFU-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']

        #mod 70,25,26
        mask=(p['PMBMOD']==70)|(p['PMBMOD']==25)|(p['PMBMOD']==26)
        mask1=(mask) & (p['POLNBTETE']==1)
        mask2=(mask) & (p['POLNBTETE']==2)
            
        p.loc[mask1,'residualTermM']= (65-p.loc[mask1,'Age1AtEntry'])*12-p.loc[mask1,'DurationIfInitial']
        p.loc[mask2,'residualTermM']=p.loc[mask2,['Age2AtEntry','Age1AtEntry']].max(axis=1)
        p.loc[mask2,'residualTermM']=((70-p.loc[mask2,'residualTermM'])*12)-p.loc[mask2,'DurationIfInitial']
     
        #mod 58 
        mask=(p['PMBMOD']==58)
        p.loc[mask,'residualTermM']=((75-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']

        #mod 1,11
        ageMaxVE=12*99
        mask=(p['PMBMOD']==11)|(p['PMBMOD']==1)
        p.loc[mask,'residualTermM']=ageMaxVE-p.loc[mask,'DurationIfInitial']       
    
        return p

#Utilisation de méthode alternatives pour le calcul des ages
    def aSupprimer_CorrAgeAtEntry(self,p):

        #mod [28,29,30,31,32,33,36, 2, 6, 7, 3, 4, 70, 25, 26, 10]
        mask=(p['PMBMOD'].isin([28,29,30,31,32,33,36, 2, 6, 7, 3, 4, 70, 25, 26, 10]))
        date1=pd.to_datetime(p.loc[mask,'CLIDTNAISS'])        
        date2=pd.to_datetime(p.loc[mask,'CLIDTNAISS2'])        
        dateDebut=pd.to_datetime(p.loc[mask,'POLDTDEB'])           
        age1=(((12*(dateDebut.dt.year-date1.dt.year)+dateDebut.dt.month-date1.dt.month+(dateDebut.dt.day/100)-(date1.dt.day/100))/12)+0.5).astype(int)
        age2=(((12*(dateDebut.dt.year-date2.dt.year)+dateDebut.dt.month-date2.dt.month+(dateDebut.dt.day/100)-(date2.dt.day/100))/12)+0.5).astype(int)  
#? A remonter
        age1[age1==0]=1

        p.loc[mask,'Age1AtEntry']=age1
        p.loc[mask,'Age2AtEntry']=age2
        
        #mod 58, 11, 1
        mask=(p['PMBMOD']==58)|(p['PMBMOD']==11)|(p['PMBMOD']==1)
        
        date1=pd.to_datetime(p.loc[mask,'CLIDTNAISS'])        
        moisnaiss1 = date1.dt.month*1        
        dateDebut=pd.to_datetime(p.loc[mask,'POLDTDEB'])       
        mask2 =(np.absolute(date1.dt.month - dateDebut.dt.month) == 6)       
        mask3 = (dateDebut.dt.day < date1.dt.day)        
        moisnaiss1[mask3 & mask2] =  moisnaiss1+1
        age1=(((12*(dateDebut.dt.year-date1.dt.year)+dateDebut.dt.month-moisnaiss1)/12)+0.5).astype(int)
        p.loc[mask,'Age1AtEntry']=age1
        p.loc[mask,'Age2AtEntry']=999
       
        return p

# Enlever des polices mod6 qui sont prise dans les réserves initiales mais pas calculée dans Prophet
    def aSupprimer_Mod6PasDansProphet(self,p):
        p.loc[p['PMBPOL'].isin([1302, 96803, 96804, 96805, 96806, 150003, 150004, 150005, 150103, 150104, 150105, 262905, 263003, 448502, 448503, 514408, 514409, 2547101]), 'Age1AtEntry'] = 999
        return p

##############################################################################################################################
#Calcul de l'âge initial (l'âge du deuxième assuré qui n'existe pas est fixé à 999)
##############################################################################################################################    

    def agesInitial(self,p):
        
        #police 1 l'age du deuxième assuré est 0 donc il né à la date début de la police (ensuite 999 ans)
        p.loc[p.POLNBTETE==1, 'CLIDTNAISS2'] = p.loc[p.POLNBTETE==1, 'POLDTDEB']
        
        date1=pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d')
        
        date2=pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d')
        
        dateDebut= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d')
        
        dtNaiss1=np.where(date1.dt.month * 100 + date1.dt.day  > dateDebut.dt.month * 100 + dateDebut.dt.day , date1.dt.year  + 1, date1.dt.year)
        
        dtNaiss2=np.where(date2.dt.month * 100 + date2.dt.day  > dateDebut.dt.month * 100 + dateDebut.dt.day , date2.dt.year  + 1, date2.dt.year)
        
        p['Age1AtEntry']=dateDebut.dt.year-dtNaiss1
        p['Age2AtEntry']=dateDebut.dt.year-dtNaiss2
        p.loc[p.Age2AtEntry==0,'Age2AtEntry']=999
        
        return p

##############################################################################################################################
#Permet d'ajouter deux colonnes avec la classPGG pour l'agrégation de la PGG (classPGG)
##############################################################################################################################    
    def allocationDesClassPGG(self,p):
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
        
        #Correction des polices Multi-taux affectées à la classe EP1.5    
        p.loc[p['PMBPOL'].isin([1751801,514407]), 'ClassPGG'] = 'EP1.5'
        
        #check toutes les polices ont une classe
        check=p['ClassPGG'].isnull().values.any()
        if check:
            sys.exit('Cetaines modalités ne sont pas affectées à une classe PGG')        
        
        return p

    def ajoutEtFormatColonnes(self,p):
        
        #Dates des calcules
        p['DateCalcul']=pd.to_datetime(p['PMBBILAN'].astype(int).astype(str)+self.moisJourCalcul)
        
        #Formatage des date en format date
        p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
        p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date
        p['CLIDTNAISS']= pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.date   
        p['CLIDTNAISS2']= pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.date
          
        #Fixation du Duration Initial par différence des mois
        p['DurationIfInitial']=((pd.to_datetime(p['DateCalcul'])-pd.to_datetime(p['POLDTDEB']))/np.timedelta64(1,'M')).apply(np.around)
 
        #Création des PM servant de base pour le calcul de la PGG
        p['PMbasePGG']=p['PMBPRVMAT']+p['PMBPBEN']+p['PMBREC']+p['PMBRECCPL']
        
        return p
 
##############################################################################################################################
#Calcul de l'échéance des polices pour obtenir la durée des projections traité par modalité
##############################################################################################################################
    def residualTermM(self,p):
    
        #Polices 1 tête,  la tête 2 est fixée à l'âge 1 pour le moment ensuite 999        
        p.loc[p['POLNBTETE']==1,'Age2AtEntry']=p.loc[p['POLNBTETE']==1,'Age1AtEntry']
        
        #Dertermination des âges limites
        ageMaxFU=65
        ageMaxAX=80
        ageMaxHO=75
        ageMaxVE=121
        ageMax29=55      
    #Traitement des mods 8
        mask=(p['PMBMOD']==8) | (p['PMBMOD']==9) 
        
        p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].max(axis=1)
        p.loc[mask,'residualTermM']=((ageMaxFU-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']
        
    #Traitement des mods 9
        mask=(p['PMBMOD']==9)    
    
        p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].min(axis=1)
        p.loc[mask,'residualTermM']=((ageMaxFU-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']
      
    #? Traitement du mod 70
        mask=(p['PMBMOD']==70)
        
        p.loc[mask,'residualTermM']=p.loc[mask,['Age2AtEntry','Age1AtEntry']].max(axis=1)
        p.loc[mask,'residualTermM']=((ageMaxAX-p.loc[mask,'residualTermM'])*12)-p.loc[mask,'DurationIfInitial']

    
    # Traitement du mod 58
        mask=(p['PMBMOD']==58)
        p.loc[mask,'residualTermM']=((ageMaxHO-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']

    #? Traitement du mod 1 et 11 (Pourquoi 121 ans age Max?)
        mask=(p['PMBMOD']==11)|(p['PMBMOD']==1)
        p.loc[mask,'residualTermM']=((ageMaxVE-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']

    
    #? Traitement du mod 29 (je sais pas si c'est bien correct)
        mask=(p['PMBMOD']==29)
        p.loc[mask,'residualTermM']=((ageMax29-p.loc[mask,'Age1AtEntry'])*12)-p.loc[mask,'DurationIfInitial']    
    
    # Traitement mod 28,29,30,31,32,33,36, 2, 6, 7, 3, 4,10 (MANQUANT)
        mask=(p['PMBMOD'].isin([28,29,30,31,32,33,36, 2, 6, 7, 3, 4, 10]))  
        mask1=(mask) & (p['POLNBTETE']==1)
        mask2=(mask) & (p['POLNBTETE']==2)
#? cette façon de faire semble correct peut-elle être appliquée aux mod 10,8,9,1,11,25,26,58,70        
        p.loc[mask1,'residualTermM']= p.loc[mask1,'POLDURC']*12-p.loc[mask1,'DurationIfInitial']      
        p.loc[mask2,'residualTermM']= p.loc[mask2,'POLDURC']*12-p.loc[mask2,'DurationIfInitial']

    #? Traitement du mod 25-26 (MANQUANT)

    

        #Replacer 999 pour les deuxièmes assurés des polices à une tête
        p.loc[p['POLNBTETE']==1,'Age2AtEntry']=999
        
        return p
    
#Cette méthode corrige les ageAtEntry de l'assuré 1 lorsqu'il y a 2 têtes avec un décalage d'age
# Attention elle doit se situer après les résidualTerm        
    def ageAtEntryDecalage(self,p):

        #mod [28,29,30,31,32,33,36, 2, 6, 7, 3, 4, 70, 25, 26]
        mask=(p['PMBMOD'].isin([28,29,30,31,32,33,36, 2, 6, 7, 3, 4, 70, 25, 26]))
        mask1=(mask) & (p['POLNBTETE']==1)
        mask2=(mask) & (p['POLNBTETE']==2)            
        
        decalage=self.decalage['DECALAGE'].to_dict()
    
        p.loc[mask2,'ageDiff']=abs(p.loc[mask2,'Age1AtEntry']-p.loc[mask2,'Age2AtEntry'])
        p.loc[mask1,'ageDiff']=p.loc[mask1,'ageDiff'].fillna(0)
        
        p['ageDecalage']=p['ageDiff'].map(decalage)
    
        p.loc[mask2,'Age1AtEntry']=np.minimum(p.loc[mask2,'Age1AtEntry'],p.loc[mask2,'Age2AtEntry'])+ p.loc[mask2,'ageDecalage']
        
        p.loc[mask,'Age2AtEntry']=999
        
        p.loc[p['residualTermM']<0,'residualTermM']=0            

        #? Replacer 999 pour les deuxièmes assurés des polices à une tête
        p.loc[p['POLNBTETE']==1,'Age2AtEntry']=999
        
        return p
    

# Ajout d'une colonne contenant les frais de fractionnement        
    def fraisFractionnement(self,p):
    
        mask12=(p['PMBFRACT']==12)
        mask6=(p['PMBFRACT']==6)
        mask4=(p['PMBFRACT']==4)
        mask2=(p['PMBFRACT']==2) 
        
        maskAX=(p['PMBMOD']==70)
        
        p.loc[mask12 & maskAX,'fraisFract']=1.08
        p.loc[mask6 & maskAX,'fraisFract']=1.06
        p.loc[mask4 & maskAX,'fraisFract']=1.05
        p.loc[mask2 & maskAX,'fraisFract']=1.04
        
#? est-ce que cela correspond avec les vrai taux de frais de fractionnement ?        
        mask=(p['PMBMOD'].isin([25, 26, 2, 6, 10]))
        
        p.loc[mask12 & mask,'fraisFract']=1.05
        p.loc[mask6 & mask,'fraisFract']=1.04
        p.loc[mask4 & mask,'fraisFract']=1.03
        p.loc[mask2 & mask,'fraisFract']=1.02
        
        
        p.loc[:,'fraisFract']=p.loc[:,'fraisFract'].fillna(1)
        
        return p
    

# Cette méthode crée toutes les colonnes en lien avec des taux de chargement    
    def ajoutLoadings(self,p):
    
        l=self.loading
        
        #Contrôle si tout les produits sont pris en compte dans les loadings    
        # df1=l[['PMBMOD','POLTARIF']].groupby(['PMBMOD','POLTARIF']).sum()
        # df2=p[['PMBMOD','POLTARIF']].groupby(['PMBMOD','POLTARIF']).sum()
        # check=df1.equals(df2)
        # if not check:
        #     sys.exit('Il manque des chargements dans Loading.xlsx')
        
        p['LoadingID']=p['PMBMOD'].astype(int).map(str) + p['POLTARIF'].map(str)
        l['LoadingID']=l['PMBMOD'].map(str)+l['POLTARIF'].map(str)
        l=l.set_index('LoadingID')
    
        #Chargement de Zillmérisation
# ? Ne manque-t-il pas certain taux dse zillmerisation (ex mod36) 
        zill=l['Zillmer'].to_dict()   
        p['tauxZill']=p['LoadingID'].map(zill)
        p['tauxZill'] = p['tauxZill'].fillna(0)
        
        #Chargement d'aquisition Alpha 1    
        alpha1=l['Alpha1'].to_dict()   
        p['aquisitionLoading']=p['LoadingID'].map(alpha1)
            
        #Chargement d'aquisition Alpha 2 (deuxième année)   
        alpha2=l['Alpha2'].to_dict()   
        p['aquisitionLoadingYear2']=p['LoadingID'].map(alpha2)       
        
        #Chargement d'aquisition Alpha 3 (troisième année)   
        alpha3=l['Alpha3'].to_dict()   
        p['aquisitionLoadingYear3']=p['LoadingID'].map(alpha3)   
    
        #Cas particuliers des Alpha
        mask=(p['PMBMOD'].isin([28,29,32]))
        p.loc[mask,'aquisitionLoading']= (p.loc[mask,'aquisitionLoading'] * np.minimum(p.loc[mask,'POLDURC'], 20) /20)    
        p.loc[mask,'aquisitionLoadingYear2']= (p.loc[mask,'aquisitionLoadingYear2'] * np.minimum(p.loc[mask,'POLDURC'], 20) /20) 
    
        mask=(p['PMBMOD'].isin([33]))
        p.loc[mask,'aquisitionLoading']= (p.loc[mask,'aquisitionLoading'] * np.minimum(p.loc[mask,'POLDURC'], 25) /25)    
        p.loc[mask,'aquisitionLoadingYear2']= (p.loc[mask,'aquisitionLoadingYear2'] * np.minimum(p.loc[mask,'POLDURC'], 25) /25)    
        p.loc[mask,'aquisitionLoadingYear3']= (p.loc[mask,'aquisitionLoadingYear3'] * np.minimum(p.loc[mask,'POLDURC'], 25) /25) 
        
        #Chargement de gestion Beta 1
        beta1=l['Beta1'].to_dict()   
        p['gestionLoading']=p['LoadingID'].map(beta1)    
    
        #Chargement de gestion Beta 2
        beta2=l['Beta2'].to_dict()   
        p['gestionLoadingSA']=p['LoadingID'].map(beta2)    
     
        #Chargement de gestion Beta 3
        beta3=l['Beta3'].to_dict()   
        p['fraisGestDureePrimesSA']=p['LoadingID'].map(beta3)    
    
        #Chargement de gestion Beta 4
        beta4=l['Beta4'].to_dict()   
        p['fraisGestDureePoliceSA']=p['LoadingID'].map(beta4)
        
    #Traitement des cas particuliers
        #Cas particuliers des Alpha
        mask=(p['PMBMOD'].isin([28,29,32]))
        p.loc[mask,'aquisitionLoading']= (p.loc[mask,'aquisitionLoading'] * np.minimum(p.loc[mask,'POLDURC'], 20) /20)    
        p.loc[mask,'aquisitionLoadingYear2']= (p.loc[mask,'aquisitionLoadingYear2'] * np.minimum(p.loc[mask,'POLDURC'], 20) /20) 
    
        mask=(p['PMBMOD'].isin([33]))
        p.loc[mask,'aquisitionLoading']= (p.loc[mask,'aquisitionLoading'] * np.minimum(p.loc[mask,'POLDURC'], 25) /25)    
        p.loc[mask,'aquisitionLoadingYear2']= (p.loc[mask,'aquisitionLoadingYear2'] * np.minimum(p.loc[mask,'POLDURC'], 25) /25)    
        p.loc[mask,'aquisitionLoadingYear3']= (p.loc[mask,'aquisitionLoadingYear3'] * np.minimum(p.loc[mask,'POLDURC'], 25) /25) 
       
        #Cas particuliers des Beta   
        #Mod 1 et 11
        mask=(p['PMBMOD'].isin([11,1]))
        mask53= (p['Age1AtEntry'] < 53) & mask
        mask70=(p['Age1AtEntry'] >= 70) & mask
    
        beta1_53=l['Beta1Age53'].to_dict()
        beta1_70=l['Beta1Age70'].to_dict()      
        p.loc[ mask53, 'gestionLoading'] = p.loc[mask53, 'LoadingID'].map(beta1_53)  
        p.loc[mask70, 'gestionLoading'] = p.loc[mask70, 'LoadingID'].map(beta1_70)    
    
        beta3_53=l['Beta3Age53'].to_dict()
        beta3_70=l['Beta3Age70'].to_dict()      
        p.loc[ mask53, 'fraisGestDureePrimesSA'] = p.loc[mask53, 'LoadingID'].map(beta3_53)  
        p.loc[mask70, 'fraisGestDureePrimesSA'] = p.loc[mask70, 'LoadingID'].map(beta3_70)
    
        beta4_53=l['Beta4Age53'].to_dict()
        beta4_70=l['Beta4Age70'].to_dict()      
        p.loc[ mask53, 'fraisGestDureePoliceSA'] = p.loc[mask53, 'LoadingID'].map(beta4_53)  
        p.loc[mask70, 'fraisGestDureePoliceSA'] = p.loc[mask70, 'LoadingID'].map(beta4_70)
        
        # Mod3 2têtes
        mask=(p['PMBMOD'].isin([3])) & (p['POLNBTETE'] == 2)
    
        beta3_h2=l['Beta3head2'].to_dict()
        beta4_h2=l['Beta4head2'].to_dict()
        p.loc[mask, 'fraisGestDureePrimesSA'] = p.loc[mask, 'LoadingID'].map(beta3_h2)   
        p.loc[mask, 'fraisGestDureePoliceSA'] = p.loc[mask, 'LoadingID'].map(beta4_h2)
    
        return p
    
# Corrige l'ensemble des primes à 0 pour les polices réduites et met le fractionement annuel
    def zeroPremiumForReducePolicy(self,p):
        
        mask = (p['PMBMOD'].isin([28,29,30,31,32,33,36,2,10,6,7, 11, 1]))  
        
        mask4_5_9_0 = (p['POLSIT']==4) | (p['POLSIT']==9) | (p['PMBFRACT']==0) | (p['PMBFRACT']==5)
        
        p.loc[mask &  mask4_5_9_0 ,'POLPRTOT']=0
        
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL1']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL2']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL3']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL4']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL5']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL6']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL7']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL8']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPL9']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPLA']=0  
        p.loc[mask &  mask4_5_9_0 ,'POLPRCPLB']=0
        p.loc[mask &  mask4_5_9_0 ,'POLPRVIEHT']=0
        
        #Ajout du fractionnement annuel pour les polices sans fractionnment
        p.loc[mask & (p['PMBFRACT']==0) , 'PMBFRACT'] = 1
        
        return p
            
           
##############################################################################################################################
#Permet de formater la dataframe du portefeuille des polices avant d'entrer dans la classe Hypo
#traitement des anomalies et mise en forme des colonnes
##############################################################################################################################

    def portfolioPreProcessing(self,p):
    
        #!! Réplication des erreurs dans les données du portefeuille
        p=self.aSupprimer_DataError(p)

        # Définition des Ages d'entrée
        p=self.agesInitial(p)
        
        #Formatage des colonnes et création des colonnes utiles    
        p=self.ajoutEtFormatColonnes(p)
        
        #!! Réplication des DCS pour le DurationIfInitial
        p=self.aSupprimer_FixationDeLaDurationInitiale(p)

        #Création des collones pour l'agragation de la PGG
        p=self.allocationDesClassPGG(p)
       
        #!! Réplication de l'erreur d'affectation des classesPGG pour les Mixtes         
        p=self.aSupprimer_ReAllocClassPGG_Mixte(p)
     
        #Nombre de mois de projection selon la date de fin des polices
        p=self.residualTermM(p)
           
        #!! Réplication des ages et policy terme selon Prophet
        p=self.aSupprimer_CorrAgeAtEntry(p)
        p=self.aSupprimer_CorrResidualTermM(p)
        
        #Création des décalages d'ages pour les polices 2 têtes de certaines modalités
        p=self.ageAtEntryDecalage(p)
            
        #Ajout d'une colonne contenant les frais de fractionnement
        p=self.fraisFractionnement(p)

        # Ajout des colonnes avec les chargements
        p=self.ajoutLoadings(p)

        # Ajustement des fractionnements pour des polices avec frac = 0 (réduites)
        p=self.zeroPremiumForReducePolicy(p)
        
        #!! ? On enlève les 18 polices que prophet ne prenait pas en compte pour les mod6
        p=self.aSupprimer_Mod6PasDansProphet(p)
             
        return p        
  

# =============================================================================
# Création de la class Hypothèse
# =============================================================================
class Hypo:
    

    def __init__(self,inputs=Inputs(), \
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        
        self.inputs=inputs
        
        if PortfolioNew:
            self.tout=self.inputs.clean()[2]
            self.p=self.inputs.clean()[2]
        else:
            self.tout=self.inputs.clean()[3]
            self.p=self.inputs.clean()[3]
        
        self.h0=self.inputs.clean()[0]
        self.h1=self.inputs.clean()[1]
        
        self.runs=self.inputs.clean()[4]
        self.shape=list(self.one().shape)
        self.SinistralityNew=SinistralityNew
        self.LapseNew=LapseNew
        self.CostNew=CostNew
        self.RateNew=RateNew

# =============================================================================
    ### METHODES DE DIMENSSIONEMENT
# =============================================================================

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
        nbrPeriodes= int(self.p['residualTermM'].max()+2)
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
        myShape[2]=int(len(self.inputs.allRuns))
        result=np.zeros(myShape)
        return np.copy(result)
    
# Retourne une template formaté pour tous les runs de 1   
    def oneAllrun(self):             
        myShape=self.shape
        myShape[2]=int(len(self.inputs.allRuns))
        result=np.ones(myShape)
        return np.copy(result)


# Retourne une template avec les années chaque mois
    def templateAllYear(self):
        model=pd.date_range(start=self.p['DateCalcul'].min(), periods=int(self.p['residualTermM'].max()+2), freq='M')
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

# =============================================================================
    ### METHODES DES HYPOTHESES
# =============================================================================
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
        
        commissionsRates=h.iloc[61:86,1:7]
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
              
        return inflationRate**(increment/12)

# =============================================================================
    ### METHODES CALCUL DES PRODUITS
# =============================================================================
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
   ### DEBUT DES TESTS
##############################################################################################################################

# a=Inputs().portfolioExtractionToCSV()
# b=a.groupby(['PMBMOD','POLTARIF']).sum()
# b.to_excel("check.xlsx", header = True )
# myHypo=Hypo()

# myHypo.mod([11])
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

