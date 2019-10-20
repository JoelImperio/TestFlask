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

#Extraction du portefeuille de polices
    
#portfolioExtractionToCSV()


#Inputs global
dateCalcul='20181231'
dateFinCalcul='20521231' #A mon avis doit être remplacer par date expiration des polices







#Permet de crée une colonne avec la classPGG
def allocationClassPGG(p):
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
    
#Calcul de l'âge initial
def agesInitial(p):
    
    date1=pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d')
    
    date2=pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d')
    
    dateDebut= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d')
    
    dtNaiss1=np.where(date1.dt.month * 100 + date1.dt.day  > dateDebut.dt.month * 100 + dateDebut.dt.day , date1.dt.year  + 1, date1.dt.year)
    
    dtNaiss2=np.where(date2.dt.month * 100 + date2.dt.day  > dateDebut.dt.month * 100 + dateDebut.dt.day , date2.dt.year  + 1, date2.dt.year)
    
    p['Age1AtEntry']=dateDebut.dt.year-dtNaiss1
    p['Age2AtEntry']=dateDebut.dt.year-dtNaiss2
    p.loc[p.Age2AtEntry==0,'Age2AtEntry']=999


#Permet de formater la dataframe des polices avant d'entrer dans la classe
def portfolioPreProcessing(p):

#Traitement des anomalies dans les données

    #Certaines dates d'échéances tombe un jour qui n'existe pas
    p.loc[p['PMBPOL'].isin([1602101,609403,2161101,2162601,297004]), 'POLDTEXP'] = '20190228'
    
    #Lorsque la police a une tête l'age du deuxième assuré est 0 donc il né à la date début de la police (ensuite 999 ans)
    p.loc[p.POLNBTETE==1, 'CLIDTNAISS2'] = p.loc[p.POLNBTETE==1, 'POLDTDEB']

    agesInitial(p)

#Formatage des colonnes et création des colonnes utiles    

    p['DateCalcul']=pd.to_datetime(dateCalcul)

##On pense que la solution en commentaire est meilleure mais ptophet effectue l'autre
#    p['DateFinCalcul']=p['POLDTEXP']
    p['DateFinCalcul']=pd.to_datetime(dateFinCalcul)
    
    p['POLDTDEB']= pd.to_datetime(p['POLDTDEB'].astype(str), format='%Y%m%d').dt.date
    p['POLDTEXP']= pd.to_datetime(p['POLDTEXP'].astype(str), format='%Y%m%d').dt.date
    p['CLIDTNAISS']= pd.to_datetime(p['CLIDTNAISS'].astype(str), format='%Y%m%d').dt.date
    

     
    p['CLIDTNAISS2']= pd.to_datetime(p['CLIDTNAISS2'].astype(str), format='%Y%m%d').dt.date
   
    
    p['ProjectionMonths']=((pd.to_datetime(p['DateFinCalcul'])-pd.to_datetime(p['DateCalcul']))/np.timedelta64(1,'M')).apply(np.ceil)
    
##On pense que la différence en mois est plus correct que le calcul des DCS pour les duration IF
#    p['DurationIfInitial']=((pd.to_datetime(p['DateCalcul'])-pd.to_datetime(p['POLDTDEB']))/np.timedelta64(1,'M')).apply(np.around)
    p['DurationIfInitial']=(pd.to_datetime(p['DateCalcul']).dt.year - pd.to_datetime(p['POLDTDEB']).dt.year)*12 \
    + pd.to_datetime(p['DateCalcul']).dt.month - pd.to_datetime(p['POLDTDEB']).dt.month + 1  
    
    allocationClassPGG(p)


    
    return p



##############################################################################################################################


##############################################################################################################################
        
    
##############################################################################################################################
##############################################################################################################################




##############################################################################################################################
#CHARGEMENT DES FICHIERS INPUTS
#- Hypothèses N et N-1
#- Portefeule N et N-1
def chargementINPUTS(PortefeuilleEtHypothèses):
    return self,PortefeuilleEtHypothèses
##############################################################################################################################

hypN=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
hypN_1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

porN=pd.read_csv(path+'/Portefeuille\Portfolio.csv')
porN=portfolioPreProcessing(porN)

porN_1=pd.read_csv(path+'/Portefeuille\Portfolio.csv')
porN_1=portfolioPreProcessing(porN_1)
   

##############################################################################################################################
##############################################################################################################################


#Importation d'une intance de Portfolio
#pol=Portfolio()

#Création de la class Hypothèse

class Hypo:
    
    ageNan=999
    allRuns=[0,1,2,3,4,5]    
    __slot__=('un','vide','zero','run','shape')

    def __init__(self,hy=hypN,hy1=hypN_1,po=porN, po1=porN_1,\
                 Run=allRuns, hypoNew=True, portfolioNew=True):
        
        if portfolioNew:
            self.tout=po 
            self.p=po
        else:
            self.tout=po1
            self.p=po1
            
        self.runs=Run
        self.un=self.one()
        self.zero=self.zeros()
        self.vide=self.vides()
        self.template= self.templateProjection()
        self.shape=list(self.un.shape)


################################################     

        if hypoNew:
            self.h=hy
        else:
            self.h=hy1

        self.securityMarginMarge=1+self.h.iloc[53,2]
        self.securityMarginBio=1+self.h.iloc[54,2]

################################################  

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
        
# Retourne une template formaté pour tous les runs avec des 0  
    def templateAllrun(self):             
        myShape=self.shape
        myShape[2]=int(len(self.allRuns))
        result=np.zeros(myShape)
        return np.copy(result)
    
# Retourne une template formaté pour tous les runs de 1   
    def oneAllrun(self):             
        myShape=self.shape
        myShape[2]=int(len(self.allRuns))
        result=np.ones(myShape)
        return np.copy(result)


# Retourne une template avec les années chaque mois
    def templateAllYear(self):
        
        model=self.template
        model=model.copy()
        model.columns=model.columns.year
        return model.transpose()
    
# Retourne les frais de gestion par police
    def fraisGestion(self):
        
        fixfee=self.h.iloc[49,3]
        
        adminCost=self.templateAllrun()
        
        adminCost[:,:,:4]=fixfee
        adminCost[:,:,4]=fixfee*self.securityMarginMarge
        adminCost[:,:,5]=fixfee*self.securityMarginBio
        #Dimensionner pour les runs en appel    
        adminCost=adminCost[:,:,self.runs] 
        
        return adminCost
    
    
    def fraisGestionPlacement(self):
        
        fixfee=self.h.iloc[50,3]

        investCost=self.templateAllrun()
        
        investCost[:,:,:4]=fixfee
        investCost[:,:,4]=fixfee*self.securityMarginMarge
        investCost[:,:,5]=fixfee*self.securityMarginBio
        #Dimensionner pour les runs en appel    
        investCost=investCost[:,:,self.runs]
        
        return investCost
    
    def templateSinistrality(self,a):
        
        bestEstimate=self.h.iloc[a,3]
        bePlusMarge=self.h.iloc[a,4]
        bioEtFrais=self.h.iloc[a,5]

        sin=self.templateAllrun()
        
        sin[:,:,:4]=bestEstimate
        sin[:,:,4]=bePlusMarge
        sin[:,:,5]=bioEtFrais
        #Dimensionner pour les runs en appel    
        sin=sin[:,:,self.runs]
        
        return sin

    def ipt(self):
        return self.templateSinistrality(14)
    def dcAccident(self):
        return self.templateSinistrality(15)
    def exo(self):
        return self.templateSinistrality(16)
    def itt(self):
        return self.templateSinistrality(17)
    def hospi(self):
        return self.templateSinistrality(18)
    def dc(self):
        return self.templateSinistrality(19)
    def fraisVisite(self):
        return self.templateSinistrality(20)
    
# Cette fonction retourne un vecteur avec les taux d'intérêt mensuel 
    def rate(self):
      
        rates=self.templateAllrun()       
        model=self.templateAllYear()
        model=model.iloc[:self.shape[1]]
        
        allrates=self.h.iloc[2:6,1:39].transpose()
        
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

# Taux de pd annuel pour chaque mois de projection   
    def pbRate(self):
        
        fixratePB=self.h.iloc[45,2]/100
        
        rate=self.rate()
        
        ratesPB=((1+rate)**12-1)-fixratePB
        
        return ratesPB

# Taux de rachat (selon le fractionnement) dimensionné pour les runs et polices lorsqu'un lapse est possible (uniquement le mois avant un paiement de prime)  
    def lapse(self):

 
        lapseSensiMoins=self.h.iloc[56,2]
        lapseSensiPlus=self.h.iloc[57,2]       
        cl=self.p['ClassPGGinit']
        
        lapseRates=self.h.iloc[23:32,1:12]
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

        
        mylapse[:,:,[3,5]]=mylapse[:,:,[3,5]]*lapseSensiMoins
        mylapse[:,:,2]=mylapse[:,:,2]*lapseSensiPlus
       
        #Dimensionner pour les runs et le portefeuille en appel    
        mylapse=mylapse[:,:,self.runs]
        
        #Prise en compte du taux fractionnel et de la mise en place avant un paiement
        mylapse=1-(1-mylapse)**(1/self.frac())
        
        mylapse= self.isLapse()*mylapse
        
        return mylapse

# Taux de réduction (anual rate) dimensionné pour les runs et polices  
    def reduction(self):

# A vérifier si même sensibilité que rachat 
        lapseSensiMoins=self.h.iloc[56,2]
        lapseSensiPlus=self.h.iloc[57,2] 
        
        cl=self.p['ClassPGGinit']
        reductionRates=self.h.iloc[34:43,1:12]
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
        
        return myReduction

# Taux de commissions (anual rate) dimensionné pour les runs et polices (inclus les commissions de gestion)     
    def commissions(self):
        
        cl=self.p['PMBMOD']
        
        commissionsRates=self.h.iloc[61:85,1:7]
        commissionsRates.columns = commissionsRates.iloc[0]
        commissionsRates=commissionsRates.drop(commissionsRates.index[0])
        commissionsRates=commissionsRates.set_index('Modalité').transpose()
        commissionsRates=commissionsRates[cl].transpose().to_numpy()
        commissionsRates=commissionsRates[:,:,np.newaxis,np.newaxis]
        
        dur=self.durationIf()      
        dur=dur[:,:,0][:,:,np.newaxis]*self.oneAllrun()    

        condlist = [dur<12,dur<24,dur<36, \
                    dur<48,dur>=48]
        
        choicelist = [commissionsRates[:,0,:],commissionsRates[:,1,:],commissionsRates[:,2,:], \
                      commissionsRates[:,3,:],commissionsRates[:,4,:]]
        
        myCommissions=np.select(condlist, choicelist)
        
        #Dimensionner pour les runs et le portefeuille en appel
        myCommissions=myCommissions[:,:,self.runs]
        
        return myCommissions

#Taux mensuel d'inflation dimensionné pour les runs et polices

    def inflation(self):
        
        inflationRate=self.h.iloc[55,2]
        
        inflationRate=inflationRate+self.un
        
        increment=np.arange(0,self.shape[1])[np.newaxis,:,np.newaxis]
            
        inflationMensuel= inflationRate**(increment/12)
        
        
        return inflationMensuel
    
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

#Retourn une matrice avec le fractionnement constant   
    def frac(self):
        
        fract = self.un * self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        return fract

#Retourn un 1 lorsqu'il y a un lapse possible    
    def isLapse(self):
        lapse = self.zeros()
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
        
        payement = self.zeros()
        check1 = (self.frac() * (self.durationIf() + 11) /12)
        check2 = np.floor((self.frac() * (self.durationIf() + 11) /12))

        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [payement[:,:,:]==0, payement[:,:,:] ==1 ]
        
        myPayement=np.select(condlist, choicelist)
        
        # Le premier mois il n'y a pas de payement car la prime est payé en début de mois et les date de calcul sont en fin de mois
        myPayement[:,0,:] = 0
        
        return myPayement

##############################################################################################################################
##############################################################################################################################
        
    
##############################################################################################################################
##############################################################################################################################





#Création de la class Portefeuille

class Portfolio(Hypo):
    
    def __init__(self,hy=hypN,hy1=hypN_1,po=porN, po1=porN_1,\
                 Run=[0,1,2,3,4,5], hypoNew=True, portfolioNew=True):      
        super().__init__()


#####DEBUT DES VARIABLES DE CALCUL DES PROJECTIONS#################################################
    
#Retourne le vecteur des ages pour l'assuré 1 ou 2 (defaut assuré 1)   
    def age(self,ass=1):

        ageInitial=self.p['Age{}AtEntry'.format(ass)].to_numpy()        
        ageInitial=ageInitial[:,np.newaxis,np.newaxis]
        
        duration=self.durationIf()-1
        duration=(duration-np.mod(duration,12))/12
        
        age=self.zero       
        age=age+ageInitial         
        age=np.where(age==self.ageNan,age,age+duration)

        return age

#Retourne un vecteur des qx dimensionné correctement pour une table de mortalité, 
# une expérience (100 = 100% de la table) et pour l'assuré 1 ou 2  
    def qx(self,table=EKM05i, exp=100, ass=1):
         
        mt=MortalityTable(nt=table, perc=exp)
        
        aQx=pd.DataFrame(mt.qx).to_numpy()
        
        myAge=(self.age(ass)).astype(int)
        myAge=np.where(myAge>mt.w,mt.w-1,myAge)
        
        myQx=np.take(aQx,myAge)
        
        #Lorsque l'âge est à 999 ans le qx est forcé à 0
        return np.where(self.age(ass) == self.ageNan,0,myQx)
    
    def qxExp(self,tableExp=EKM05i, assExp=1):
        
        qx=self.qx(table=tableExp,ass=assExp)*self.dc
        
        return qx
    
    
#Retourn la probabilité de décès mensuelle
    def qxMens(self,tableM=EKM05i, expM=100, assM=1):
        
        qx=1-(1-self.qx(table=tableM,exp=expM,ass=assM))**(1/12)
        
        qx[:,0,:] = 0
        
        return qx
    
#Retourn la probabilité jointe de décès mensuel
    def qxyMens(self,tableXY=EKM05i, expXY=100):
        
        qx=self.qxMens(tableM=tableXY, expM=expXY, assM=1)
        
        qy=self.qxMens(tableM=tableXY, expM=expXY, assM=2)
        
        return qx+qy-qx*qy
        






##############################################################################################################################
##############################################################################################################################
        
    
##############################################################################################################################
##############################################################################################################################


    

#####ICI pour faire des tests sur la class##########################################################

def testerHypo():
    return 0

myRun=[1,5]
#myRun=[0,1,2,3,4,5]


myHypo=Hypo(Run=myRun)

myHypo.mod([8,9])
#myHypo.ids([896002])
#myHypo.groupe(['MI3.5'])


###Les fonctions de la class

#a=myHypo.tout
#b=myHypo.p
#
#c=myHypo.runs
#d=myHypo.shape
#e=myHypo.un
#f=myHypo.zero
#g=myHypo.vide
#h=myHypo.template

#i=myHypo.fraisGestion()
#j=myHypo.fraisGestionPlacement()
#k=myHypo.rate()
#l=myHypo.pbRate()
#m=myHypo.lapse()
#n=myHypo.ipt()
#o=myHypo.dcAccident()
#p=myHypo.exo()
#q=myHypo.itt()
#r=myHypo.hospi()
#s=myHypo.dc()
#t=myHypo.fraisVisite()

#u=myHypo.reduction()
#v=myHypo.commissions()
w=myHypo.inflation()




###Visualiser un vecteur np en réduisant une dimension
data=m
a=pd.DataFrame(data[:,:,1])


def testerPortfolio():
    return 0
    
#myPolicies=Portfolio()

#myPolicies.mod([8,9])
#myPolicies.ids([896002])
#myPolicies.groupe(['MI3.5'])

#Les fonctions de la class Portfolio()


#yi=myPolicies.durationIf()
#yj=myPolicies.age(1)
#yk=myPolicies.qx(table=EKM05i, exp=41.73,ass=2)
#yl=myPolicies.qxMens(tableM=EKM05i, expM=41.73,assM=2)
#ym=myPolicies.qxyMens(tableXY=EKM05i, expXY=41.73)
#yn=myPolicies.frac()
#yo=myPolicies.isPremPay()
#yp=myPolicies.isLapse()

