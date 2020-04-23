from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
from MyPyliferisk.mortalitytables import *
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

##############################################################################################################################
#Création de la class TEMP
##############################################################################################################################

    # Modalité 3 uniquement pour les 1 tête
class TE(Portfolio):
    # mods=[3]
    # modHeads = [3],1
    # complPremium=pol.p['POLPRCPL2']

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.modHead([3],1)
        
        
    
#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()
        
    
    
    def loopSaving(self):

#Variables des actifs  
# Condition me permettant de supprimer les polices qui ont un age à 999 (mis volontairement dans le preprocessing)
        nbrPolIf = self.age() < 999
        nbrPolIf = nbrPolIf * self.one()
        
        nbrPolIfSM=self.zero()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrNewRed = self.zero()
        matRate=self.zero()
        
#Variables des réduites
        nbrPupsIf=self.zero()
        nbrPupDeath=self.zero()
        nbrPupSurrender=self.zero()
        nbrPupIfSM=self.zero()
        nbrPupMaturities=self.zero()

#Variables biométriques et génériques
        lapseTiming=0.5
        polTermM=self.polTermM()       
        lapseD=lapseTiming * self.lapse()
        lapse = self.lapse()          
        qxy = self.qxExpMens() 
        qx = self.qxExp()
        
    # # Modification les mixtes 2 tetes sont en fait calculée en fonction de l'assuré 1 (Ce qui est faux) (A MODIFIER) ?
    #     mask = (((self.p['PMBMOD']==2) & (self.p['POLNBTETE']==2))).astype(bool)
    #     qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
    #     qxy[mask] = 1-(1-qxy[mask])**(1/12)
        qxyD = lapseTiming * qxy

        # Variable actuarielle
        AExn = self.AExn

        #Définition du vecteur des maturités (bool)        
        matRate[polTermM+1 ==self.durationIf()]=1 
        
# Déclaration des variables pour le calcul des PM        
        # Variable existante
        # zill = self.zero()
        # precPP = self.precPP()
        # valSaPP = self.valSaPP()
        # valNetPP = self.valNetPrem()
        # prInventPP = self.prInventaire()
        # alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
        # axn = self.axn
        # valSumAss = self.sumAss() * self.AExn
        # provGestPP = self.provGestPP()
        # pmFirstYear = self.pmFirstYear()    
        # allocMonths = self.allocMonths()
        # txPartPB = self.txPartPB()

        
        nbtete = self.p['POLNBTETE'][:,np.newaxis, np.newaxis]*self.one() 
        
        
        # # Nouvelles variables
        # valAccrbPP = self.zero()
        # pbIncorPP = self.zero()
        # pbAcquPP = self.zero()
        # pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        # pbCalcPP = self.zero()
        # isActive = self.isActive()
        # mathResPP = self.zero()  
        # provTechPP = self.zero()
        # pmZillCum = self.zero()
        # pmZillPP = self.zero()
        # pmPourPB = self.zero()
        # tierPM = self.zero()
        # zillTot = self.zero()
        # pbSortMatsPP = self.zero()
        # pbSortSurrPP = self.zero()
        # pbSortDthPP = self.zero()
        

        # # Calcul des PM au temps 0 
        # valAccrbPP[:,0,:] = pbAcquPP[:,0,:] * AExn[:,0,:] 
        
        # tierPM[:,0,:] = (1/3) * np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] + precPP[:,0,:] - valNetPP[:,0,:], 0)
            
        # zillTot[:,0,:] = np.minimum(alpha[:,0,:] * prInventPP[:,0,:] * axn[:,0,:], np.maximum(valSumAss[:,0,:] - valNetPP[:,0,:] + provGestPP[:,0,:], 0))
            
        # zill[:,0,:] = np.where((tierPM[:,0,:] <= zillTot[:,0,:]) & (nbtete[:,0,:] != 2), tierPM[:,0,:], zillTot[:,0,:])
        
        # mathResPP[:,0,:] = np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] - valNetPP[:,0,:] + precPP[:,0,:] - zill[:,0,:], 0 )

        # provTechPP[:,0,:] = mathResPP[:,0,:] - provGestPP[:,0,:] - precPP[:,0,:] + zill[:,0,:]
        
        # pmZillPP[:,0,:] = provTechPP[:,0,:] - zill[:,0,:]
        
        
        for i in range(1,self.shape[1]):

#Définition des variables des actifs            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:] - nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseD[:,i,:]))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxyD[:,i,:]))
            
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:] - nbrMaturities[:,i,:]


#Définition des variables des réduites
            nbrPupMaturities[:,i,:]=nbrPupsIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPupIfSM[:,i,:]=nbrPupsIf[:,i-1,:] - nbrPupMaturities[:,i,:]
            
            nbrPupDeath[:,i,:]=nbrPupIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseTiming*lapse[:,i,:]))
            
            nbrPupSurrender[:,i,:]=nbrPupIfSM[:,i,:]*lapse[:,i,:]*(1-(lapseTiming*qxy[:,i,:]))
            
            nbrPupsIf[:,i,:]=nbrPupsIf[:,i-1,:]-nbrPupDeath[:,i,:]-nbrPupSurrender[:,i,:] - nbrPupMaturities[:,i,:] + nbrNewRed[:,i,:]


# Variable permettant le calcul des reserves et pb

            # pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            # pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

            # valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] 
            
            # tierPM[:,i,:] = (1/3) * (np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0))
            
            # zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:], 0))
            
            # zill[:,i,:] = np.where((tierPM[:,i,:] <= zillTot[:,i,:]) & (nbtete[:,i,:] != 2), tierPM[:,i,:], zillTot[:,i,:])
            
            # mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )
            
            # provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            # pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            # pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            # pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            # pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            # pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]
            
            # pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
            # pbSortSurrPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:] * AExn[:,i,:]
            
            # pbSortDthPP[:,i,:] = pbCalcPP[:,i-1,:] * isActive[:,i,:]



#Sauvegarde des variables des actifs 
        #Nombre de polices actives                                 
        self.nbrPolIf=nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM=nbrPolIfSM
        #Nombre de décès
        self.nbrDeath=nbrDeath
        #Nombre d'annulation de contrat
        self.nbrSurrender=nbrSurrender
        #Nombre de nouvelle réduction
        self.nbrNewRed = nbrNewRed
        # Nombre de nouvelle maturités
        self.nbrNewMat = nbrMaturities
        
#Sauvegarde des variables des réduites       
        #Nombre de polices réduites                                
        self.nbrPupsIf=nbrPupsIf
        #Nombre de police réduites en déduisant les échéances du mois
        self.nbrPupIfSM=nbrPupIfSM
        #Nombre de décès de polices résuites
        self.nbrPupDeath=nbrPupDeath
        #Nombre d'annulation de contrat de polices réduites
        self.nbrPupSurrender=nbrPupSurrender
        # Nombre de police réduite arrivant à maturité
        self.nbrPupMat = nbrPupMaturities



# # Sauvegarde des variables concernant les PM
#  # Montant de PB à affecter par police
#         self.pbCalcPP = pbCalcPP
#   # PB acquise des polices actives
#         self.pbAcquPP = pbAcquPP
# # PB dfdonnée par police en cas de maturité     
#         self.pbSortMatsPP = pbSortMatsPP
# # PB donnée par police en cas de rachat
#         self.pbSortSurrPP = pbSortSurrPP
# # PM utilisée pour le calcul de la PB
#         self.pmPourPB = pmPourPB
# # PM Zillmérisée cumulée 
#         self.pmZillCum = pmZillCum
# # Provisions technique par police 
#         self.provTechPP = provTechPP
# # Reserves mathématiques par polices       
#         self.mathResPP = mathResPP
# # Valeur actualisée de la PB 
#         self.valAccrbPP = valAccrbPP
# # PB incorporée par polices       
#         self.pbIncorPP = pbIncorPP
# # Provision zillmérisée par police     
#         self.pmZillPP = pmZillPP
# # Zillmérisation 
#         self.zill = zill
# # Zillmérisation en comptant le (1/3) de la pm comme zill       
#         self.zillTot = zillTot
# # Tiers de la pm comptée comme zill       
#         self.tierPM = tierPM
# # PB donnée par police en cas de décès
#         self.pbSortDthPP = pbSortDthPP


    
# #  Retourne un vecteur de temps t (représente t dans prophet)
        
#     def time(self):
        
#         increment = np.cumsum(self.one(), axis = 1) -1
        
#         return increment
        
    
    
    
# # Vecteur qui met des 1 tout les 12 mois, sinon 0
#     def isVal(self):
        
#         check = (((self.time()%12))==11)
    
#         return check
    
    
    
#     def rep(self):
        
#         array = np.arange(self.p['Age1AtEntry'], pol.shape[1])
    
#         return array
    
      
    
#   # vecteur calcul valuation l
    
#     def l_val(self):
        
#         annValNQ = (1-self.qx(table=GKM95))*self.isVal()
        
#         return annValNQ
    
    
# #Retourne les primes pures   
#     def purePremium(self):
#         prem=pol.p['POLPRVIEHT']
#         return prem.to_numpy()[:,np.newaxis,np.newaxis]/self.frac()
    
# #Retourne les primes des garanties complémentaires    
#     def premiumPrincipal(self):
        
#         return (pol.p['POLPRCPL1']+pol.p['POLPRCPL2']+pol.p['POLPRCPL3']+pol.p['POLPRCPL4']+pol.p['POLPRCPL5']+pol.p['POLPRCPL6']+pol.p['POLPRCPLA'] ).to_numpy()[:,np.newaxis,np.newaxis]



#     def adjustedReserve(self):

#   # Age limite pour mod3
#         pol.agelimite=((pol.age()-1)<=60)
           
#         annualPrem = pol.premiumPrincipal()
#         annualPrem = annualPrem / pol.frac()   
#         riderC =  annualPrem * pol.isPremPay() *pol.dcAccident() * pol.nbrPolIfSM
#         pol.agelimite = pol.agelimite * pol.one()
#         #Calcul du risque en cours
#         riderIncPP=annualPrem*pol.agelimite*pol.isPremPay()
#         riderIncPP2=annualPrem*pol.agelimite
        
# # Ne prend pas en compte les risque en cours du modelpoint ??? à modifier
#         # precPP=(pol.p['PMBREC'] + pol.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * pol.one()
#         precPP = pol.zero()
#         frek=pol.frac()

#         for i in range(1,pol.shape[1]):
#             precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
            
#         CaFracPC=pol.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
#         CaPremPC=pol.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
#         ppureEnc = (annualPrem * (1-CaPremPC) / CaFracPC)* pol.isPremPay() *pol.nbrPolIfSM
        
#         mathResBA=np.maximum(precPP,0)
#         mathResPP=mathResBA 
#         provMathIf=mathResPP*pol.nbrPolIf
#         mathresIF=provMathIf
        
#         mathResIfcorr=pol.zero()       
#         mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]  
#         mathResIfcorr = mathResIfcorr - riderC + ppureEnc

#         reserve=mathResIfcorr
#         reserve=np.maximum(reserve,0)
        
#         return reserve
        

    
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self

pol = TE()

# Mod 3 1tete
# pol.modHead([3],1)
# pol.ids([52001])

# Mod 3 2tete
# pol.modHead([3],2)
# pol.ids([111402])



# Mod4
# pol.mod([4])
# pol.ids([301])

death = pol.nbrDeath



check=pol.nbrPolIf

monCas=check
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zJO/check.csv',header=False)


pol.p.to_excel(path+'/zJO/check portefeuille.xlsx', header = True )
