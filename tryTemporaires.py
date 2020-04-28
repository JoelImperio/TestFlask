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
    ageLimiteCPL = 60
    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.modHead([3],1)
        
        
    
#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.commutations()
        self.loopTemp()
    
# =============================================================================
# --- A REMONTER
# =============================================================================
    
 # A REMONTER (repris des mixtes) pour calcul CLAIM
# retourne la somme assurée avec le bon format
    def sumAss(self): 
        return self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one() 
    
## Fonction reprise de Produit EP (Utilisé dans claim et expenses)
# Vecteur de 1 et 0 permettant de savoir si police toujours active ou non
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask
  
# Reprise des mixtes (POUR CLAIM)
# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth ==1
        return mask*1  
  
 # Reprises des mixtes (POUR CLAIM)
 # Arrondi des tables afin d'obtenir taux pb (table rdt est). Le taux PB va également dépendre du taux d'intêret 
    def txPartPB(self):
        rate = (1+self.pbRate())**12 - 1
        rate = (1+rate)**(1/12) - 1

        # ligne à supprimer pour corriger !! il ne faut pas arrondir ce taux
        rate = np.round(rate, decimals = 6)
        
        txInt = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()/100
        return np.maximum(0, rate - txInt) 
  
 # reprise des mixtes (POUR CLAIM) 
 # Met un vecteur de 1 et 0 (1 si la police possède moins de 12 mois)
    def pmFirstYear(self):
        vec = self.one() * 12
        mask = self.durationIf() <= 12
        vec[mask] = self.durationIf()[mask]
        return vec 
     
# Reprise des Mixtes (POUR CLAIM)
# Valeur actualisé SA (Net single premium value) AExn * capital
    def valSaPP(self):
        # mask ici car au moment de l'échéance de la police, le net Single premium = 0 et non Capital
        mask = self.polTermM() > self.durationIf() 
        valSaPP = self.zero()
        valSaPP[mask] = self.AExn[mask] * self.sumAss()[mask]
        return valSaPP
    
    
# Reprise des mixtes sans le mask pour mod6 et 7 (POUR CLAIM)
# Calcul de la valeur actualisée des premiums
    def valNetPrem(self):
        return self.purePremium() * self.axn 
    
    
    
    # A corriger afin de pouvoir prendre en compte dans le futur les 2ème têtes de manière correcte (remonté quand celle-ci sera juste)
# Fonction présent dans l'update permettant de chargé une fois tous les symboles de commutation
    def commutations(self):
        
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Nxt = self.actu('Nx', 't')
        # Nxp = self.actu('Nx', 'p')
        NxDec = self.actu('Nx', 't+1')
        
        Dx = self.actu('Dx', 'x')
        Dxn = self.actu('Dx', 'n')
        Dxt = self.actu('Dx', 't')
        # Dxp = self.actu('Dx', 'p')
        DxDec = self.actu('Dx', 't+1')
        
        Mx = self.actu('Mx', 'x')
        Mxn = self.actu('Mx', 'n')
        Mxt = self.actu('Mx', 't')
        # Mxp = self.actu('Mx', 'p')
        MxDec = self.actu('Mx', 't+1')
  
# AExn
        AExn = self.zero()
        AExn[Dxt>0] = AExn[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] ) / Dxt[Dxt>0]
        AExn = np.roll(AExn, -1, axis = 1)
        
        AExnDec = self.zero()
        AExnDec[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0]) / DxDec[DxDec>0]
        AExnDec = np.roll(AExnDec, -1, axis = 1)
        
        AExn = self.interp(AExn, AExnDec)
  
# äxn annuity endowment insurance
        axn = self.zero()
        axn[Dxt>0] = (Nxt[Dxt>0] - Nxn[Dxt>0]) / Dxt[Dxt>0]
        axn = np.roll(axn, -1, axis = 1)
        
        axnDec = self.zero()
        axnDec[DxDec>0] = (NxDec[DxDec>0] - Nxn[DxDec>0]) / DxDec[DxDec>0]
        axnDec = np.roll(axnDec, -1, axis = 1)
        
        axn = self.interp(axn, axnDec)
        
    
# Calcul des variable pour des polices à 2 têtes       
        
        Nx = self.actu('Nx', 'x', nbtetes = 2)
        Nxn = self.actu('Nx', 'n', nbtetes = 2)
        Nxt = self.actu('Nx', 't', nbtetes = 2)
        NxDec = self.actu('Nx', 't+1', nbtetes = 2)
        
        Dx = self.actu('Dx', 'x', nbtetes = 2)
        Dxn = self.actu('Dx', 'n', nbtetes = 2)
        Dxt = self.actu('Dx', 't', nbtetes = 2)
        DxDec = self.actu('Dx', 't+1', nbtetes = 2)
        
        Mx = self.actu('Mx', 'x', nbtetes = 2)
        Mxn = self.actu('Mx', 'n', nbtetes = 2)
        Mxt = self.actu('Mx', 't', nbtetes = 2)
        MxDec = self.actu('Mx', 't+1', nbtetes = 2)
        

# AExn endowment insurance 2 tetes
        AExn2t = self.zero()
        AExn2t[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] ) / Dxt[Dxt>0]
        AExn2t = np.roll(AExn2t, -1, axis = 1)
        
        AExnDec2t = self.zero()
        AExnDec2t[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0])  / DxDec[DxDec>0]
        AExnDec2t = np.roll(AExnDec2t, -1, axis = 1)
        
        AExn2t = self.interp(AExn2t, AExnDec2t)
  
# äxn annuity endowment insurance 2t
        axn2t = self.zero()
        axn2t[Dxt>0] = (Nxt[Dxt>0] - Nxn[Dxt>0]) / Dxt[Dxt>0]
        axn2t = np.roll(axn2t, -1, axis = 1)
        
        axnDec2t = self.zero()
        axnDec2t[DxDec>0] = (NxDec[DxDec>0] - Nxn[DxDec>0]) / DxDec[DxDec>0]
        axnDec2t = np.roll(axnDec2t, -1, axis = 1)
        
        axn2t = self.interp(axn2t, axnDec2t)
        
        
        self.AExn = self.zero()
        self.axn = self.zero()
        

        mask2t = self.p['POLNBTETE'] == 2
        mask1t = self.p['POLNBTETE'] == 1
        
        self.AExn[mask1t] = AExn[mask1t]
        self.AExn[mask2t] = AExn2t[mask2t]
        
        
        self.axn[mask1t] = axn[mask1t]
        self.axn[mask2t] = axn2t[mask2t]
    
    
    
    
    
# 
    def loopTemp(self):

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
        lapseTiming=1
        polTermM=self.polTermM()   
        
        # Lapse timing = 1, donc on ne prend pas en compte les lapses pour le calcul des death pour ces modalité. A  modifier ?
        lapseD=(1-lapseTiming) * self.lapse()
        lapse = self.lapse()          
        qxy = self.qxExpMens() 
        qx = self.qxExp()
        
    # Modification les temporaires 2 tetes sont en fait calculée en fonction de l'assuré 1 (Ce qui est faux) (A MODIFIER) ?
        mask = (self.p['POLNBTETE']==2).astype(bool)
        qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
        qxy[mask] = 1-(1-qxy[mask])**(1/12)
        qxyD = lapseTiming * qxy

        # Variable actuarielle
        AExn = self.AExn
        axn = self.axn

        #Définition du vecteur des maturités (bool)        
        matRate[polTermM+1 ==self.durationIf()]=1 
        
# Déclaration des variables pour le calcul des PM        
        # Variable existante
        zill = self.zero()
        precPP = self.precPP()
        valSaPP = self.valSaPP()
        valNetPP = self.valNetPrem()
        prInventPP = self.prInventaire()
        alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
        
        valSumAss = self.sumAss() * self.AExn
        provGestPP = self.provGestPP()
        pmFirstYear = self.pmFirstYear()    
        allocMonths = self.allocMonths()
        txPartPB = self.txPartPB()
        duration = self.durationIf()
        
        # nbtete = self.p['POLNBTETE'][:,np.newaxis, np.newaxis]*self.one() 
        
        
        # # Nouvelles variables
        valAccrbPP = self.zero()
        pbIncorPP = self.zero()
        pbAcquPP = self.zero()
        pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pbCalcPP = self.zero()
        isActive = self.isActive()
        mathResPP = self.zero()  
        provTechPP = self.zero()
        pmZillCum = self.zero()
        pmZillPP = self.zero()
        pmPourPB = self.zero()
        # tierPM = self.zero()
        # zillTot = self.zero()
        # pbSortMatsPP = self.zero()
        # pbSortSurrPP = self.zero()
        # pbSortDthPP = self.zero()
        zill1 = self.zero()
        zill2 = self.zero()
        

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

            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

            valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] 
            
            # tierPM[:,i,:] = (1/3) * (np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0))
            
            # zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:], 0))
            
            # zill[:,i,:] = np.where((tierPM[:,i,:] <= zillTot[:,i,:]) & (nbtete[:,i,:] != 2), tierPM[:,i,:], zillTot[:,i,:])
            
            # Différence par rapport au mixtes
            zill1[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:])
            zill2[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], 0.8 * (valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:]))
            
            zill[:,i,:] = np.where(duration[:,i,:] <= 24, zill1[:,i,:], zill2[:,i,:])
            
            mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )
            
            provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]
            
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



# =============================================================================
# --- CALCUL DES PREMIUMS
# =============================================================================

# Retourne les primes complémentaires
    def premiumCompl(self):
        
        maskAge = (self.age() <= self.ageLimiteCPL)
        premium = self.p['POLPRCPL1'] + self.p['POLPRCPL2'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5'] + self.p['POLPRCPL6']\
             + self.p['POLPRCPL8'] + self.p['POLPRCPL9']
        premium = premium[:,np.newaxis, np.newaxis]*self.one()  
        total = self.zero()
        total[maskAge] = premium[maskAge] / self.frac()[maskAge]
        return total
    
# Retourne les primes annuelles
    def premInc(self):
        annualPrem = self.p['POLPRVIEHT'][:,np.newaxis, np.newaxis]*self.one() / self.frac()
        return annualPrem
    
# Retourne les primes totales perçues (Je pense qu'il faudrait remonté celle-ci pour remplacé celle existante)
    def totalPremium(self):        
        return ((self.premInc() * self.indexation()) + self.premiumCompl()) * self.nbrPolIfSM * self.isPremPay()


# calcul de la prime pure
    def purePremium(self):
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Dx = self.actu('Dx', 'x')
        Mx = self.actu('Mx', 'x')
        Mxn = self.actu('Mx', 'n')

        AExn = self.zero()
        AExn = (Mx - Mxn ) / Dx
        
        axn = self.zero()
        axn = (Nx - Nxn ) / Dx
        
        
       
        Dxt = self.actu('Dx', 't')

        
        
        return (AExn / axn)  * self.sumAss()


# Calcul de la valeur actualisée des primes
    def aduePolVal(self):
        Nx = self.actu('Nx', 'x')
        Nxp = self.actu('Nx', 'p')
        Dx = self.actu('Dx', 'x')
        return (Nx - Nxp ) / Dx


# Valeur actualisée des primes au temps 0 
    def valNetPfac(self):
        Nx = self.actu('Nx', 'x')
        Nxn = self.actu('Nx', 'n')
        Dx = self.actu('Dx', 'x')
        
        return (Nx - Nxn) / Dx


# Calcul de la prime d'inventaire
    def prInventaire(self):
        return self.purePremium() + self.p['fraisGestDureePoliceSA'][:,np.newaxis, np.newaxis] * self.sumAss() * (self.aduePolVal() / self.valNetPfac()) + self.p['fraisGestDureePrimesSA'][:,np.newaxis, np.newaxis] * self.sumAss()
        
   




# =============================================================================
# --- CALCUL DES CLAIMS
# =============================================================================

# Il n'y a pas de condition sur l'age de l'assuré ici (A MODIFIER ?)
# determine le taux de sinistralité pour les complémentaires
    def riderCRate(self):
        
        IAD = self.p['POLPRCPL1'][:,np.newaxis, np.newaxis] * self.ipt()
        dblAcc = self.p['POLPRCPL2'][:,np.newaxis, np.newaxis] * self.dcAccident()
        trplAcc = self.p['POLPRCPL3'][:,np.newaxis, np.newaxis] * self.dcAccident()
        exo = self.p['POLPRCPL4'][:,np.newaxis, np.newaxis] * self.exo()
        exoRente = self.p['POLPRCPL5'][:,np.newaxis, np.newaxis] * self.itt()
        hospi = self.p['POLPRCPL6'][:,np.newaxis, np.newaxis] * self.hospi()
        acc = self.p['POLPRCPL9'][:,np.newaxis, np.newaxis] * self.dcAccident()
        
        mask = (self.premiumCompl() > 0)
        total = self.zero()
        total[mask] = (IAD[mask] + dblAcc[mask] + trplAcc[mask] + exo[mask] + exoRente[mask] + hospi[mask] + acc[mask]) / (self.premiumCompl()[mask] * self.frac()[mask])
        
        return total

# Charges des complémentaires par polices
    def riderCost(self):
        return self.premiumCompl() * self.riderCRate() * self.isPremPay()
            

# Claim complémentaires
    def claimCompl(self):
        return self.riderCost() * self.nbrPolIfSM


# Calcul de la provision de gestion
    def provGestPP(self):
        return self.zero()

# Pris des Epargne (S'appelle riskEnCours) (POUR CLAIM) (N'est pas exactement la même formule mais presque, à voir si on la remonte)
#Retourne le risque en cours
    def precPP(self):

        frek=self.frac()
          
        premCompl =  self.premiumCompl()/frek 
        
        #Calcul du risque en cours
        riderIncPP=premCompl*self.isPremPay()
        riderIncPP2=premCompl   
        precPP = self.zero()
        
# A rajouté pour corrigé les risque en cours 
        # precPP[:,0,:] = pol.p['PMBREC'].to_numpy()[:,np.newaxis] 

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
              
        return precPP
    
    
# Calcul claim prrincipale
    def claimPrincipal(self):
        return self.sumAss() * self.nbrDeath
    
    

# =============================================================================
# --- CALCUL DES EXPENSES
# =============================================================================

#  calcul des provisions techniques ajustée (PROV_TECH_AJ)
    def provTechAj(self):
        provTechAj = self.zero()
        provTechIf = self.provTechIf()
        primeInvest = self.prPure() * self.nbrPolIfSM * self.isPremPay() / self.frac()
        riderCoutgo = self.claimCompl()
        tresRldMat = self.tresRldMat()
        pbIncorpIf = self.pbIncorpIF()
        
        for i in range(1,self.shape[1]):
            provTechAj[:,i,:] = provTechIf[:,i-1,:] + pbIncorpIf[:,i,:] + primeInvest[:,i,:] - riderCoutgo[:,i,:] - tresRldMat[:,i,:]
        return provTechAj




  # calcul des intêret techniques crédités (INT_CRED_T) 
    def totIntCred(self):
        
# intêrets techniques crédité        
        intCredT = (self.txInt()-1) * self.provTechAj()
        intCredT[:,0,:] = 0
        return intCredT


# # loop pour calculer les reserves pour expense ADJ_MATHRES2
    def reserveForExp(self):
        
          # déclaration des nouvelles variables
          # resReldMat = self.zero()
          # totExp = self.zero()
           rfinAnn = self.zero()
           oTaxblInc = self.zero()
          # adjMathRes2 = self.zero()
           resFinMois = self.zero()
          # provMathAj = self.zero()
          reprisePB = self.zero()
        
        
          # Nombre polices
          # nbrPolIf = self.nbrPolIf
          # noMat = self.nbrNewMat
 
          # fonction existantes
          # fMathResIF = self.provMathIf() + self.fondPB()
          # provMathIf = self.provMathIf()
          # riderCoutgo = self.claimCompl()
          # pbIncorpIF = self.pbIncorpIF()
          # premInc = self.totalPremium()

          # fondPB = self.fondPB()
          # mUfii = self.mUfii()
          # repPbMats = self.repPbMats()
          # premInvest = self.prPure() * self.nbrPolIfSM * self.isPremPay() / self.frac()
          # les primes investies sont à 0 pour les modalité à primes unique
          # premInvest[self.p['PMBMOD'].isin([6,7])] = self.zero()[self.p['PMBMOD'].isin([6,7])]
          # unitExp = self.unitExpense()
      
          # dotationPB = self.dotationPB()
          # pbSortie = self.pbSortie()
           totIntCred = self.totIntCred() 
          # txReserve = self.fraisGestionPlacement()
          # mathresPP = self.mathResPP  
          # totComm = self.totalCommissions()
          # monthPb = self.one() - self.allocMonths()
          # isActive = self.isActive()
      
          for i in range(1,self.shape[1]):
            
              # resReldMatTEMP =  (fondPB[:,i-1,:] + rfinAnn[:,i-1,:])
            
              # resReldMat[:,i,:] = np.divide(resReldMatTEMP, (nbrPolIf[:,i-1,:]), out=np.zeros_like(resReldMatTEMP), where=(nbrPolIf[:,i-1,:])!=0)\
              #     * noMat[:,i,:] + mathresPP[:,i-1,:] * noMat[:,i,:] 
            
              # adjMathRes2[:,i,:] = fMathResIF[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:] - resReldMat[:,i,:] - repPbMats[:,i,:]
        
              # totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
                
              # provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + pbIncorpIF[:,i,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - (totExp[:,i,:] + totComm[:,i,:]) - resReldMat[:,i,:]
        
              # oTaxblInc[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            
               resFinMois[:,i,:] = oTaxblInc[:,i,:] + reprisePB[:,i,:] - totIntCred[:,i,:] - pbIncorpIF[:,i,:] - dotationPB[:,i,:] - pbSortie[:,i,:]
            
               rfinAnn[:,i,:] = (rfinAnn[:,i-1,:] + resFinMois[:,i,:]) * monthPb[:,i,:] * isActive[:,i,:]
            
    #Définition des variables récursives
            
          # Résultat financier en fin de mois non constaté
          self.resFinMois = resFinMois
          # Résultat de l'année en cours non constaté
          self.rfinAnn=rfinAnn
          # Reserves mathématiques ajustées pour calculer les expenses
          self.adjMathRes2 = adjMathRes2
          # Office taxable Income
          self.oTaxblInc = oTaxblInc
          # Provisions mathématiques ajustées
          self.provMathAj = provMathAj
          # diminution des reserves à la maturité
          self.resReldMat = resReldMat
          # prime investie
          self.premInvest = premInvest
          # Provisions mathématiqwues
          self.fMathResIF = fMathResIF
          # total expenses 
          self.totExp = totExp



    
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self

pol = TE()

# Mod 3 1tete
# pol.modHead([3],1)
# pol.ids([52001])

# pol.ids([171803])

# Mod 3 2tete
# pol.modHead([3],2)
# pol.ids([111402])



# Mod4
# pol.mod([4])
# pol.ids([301])



pol.mod([4,3])


death = pol.nbrPolIf



check=pol.unitExpense()

monCas=check
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zJO/check.csv',header=False)


pol.p.to_excel(path+'/zJO/check portefeuille.xlsx', header = True )
