from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
# from MyPyliferisk import Actuarial
# from MyPyliferisk.mortalitytables import *
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()


# =============================================================================
# Création de la class Epargne
# =============================================================================

class MI(Portfolio):
    mods=[2,10,6,7]


#Products: F1XT_1,F2XT_1,F1XT14,F1XT11
    
    # age limite pour la garantie complémentaire CPL1
    ageLimiteCPL1 = 60
    ageLimiteCPL2 = 65

    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.commutations()
        self.loopSaving()
        self.reserveForExp()

# =============================================================================
    ### FONCTION A REMONTER
# =============================================================================

# Vient de EP()
# Calcul des expenses venant des reserves (les frais de gestion des placements) (EXPENSES)
    def reserveExpense(self):
        reserveExpense = self.adjMathRes2 * self.fraisGestionPlacement()
        return reserveExpense
    

# Celle-ci vient aussi de produit EP, je pense qu'on peut remplacé celle qui existe dans portefeuille (la différence est qu'ici il y a nbrPupIfSM 
# et celui-ci est à 0 dans les mixtes, funérailles...) A tester si cela ne casse pas les produits déjà existant (EXPENSES)
# Retourne le coût par police pour les polices avec réduction possible (RENEXP_XRSE) 
    def unitExpense(self):
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        coutParPolice=self.fraisGestion()
        cost=coutParPolice*inflation*(self.nbrPolIfSM + self.nbrPupIfSM)
        return cost

## Fonction reprise de Produit EP (CLAIM)
# ici on détermine le capital pour Protection d'avenir en fonction de l'âge
    def capPA(self):
        capPA = self.zero()
        capPA[self.age() <= 55]= 25000
        capPA[self.age() > 55]= 5000
        capPA[self.age() > 65]= 0
        capPA[self.p['POLPRCPL9'] == 0]=0
        return capPA

## Fonction reprise de Produit EP (Utilisé dans claim et expenses)
# Vecteur de 1 et 0 permettant de savoir si police toujours active ou non
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask

## Fonction reprise de Produit EP (EXPENSES)
# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth ==1
        return mask*1
    
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
  
# AExn endowment insurance
        AExn = self.zero()
        AExn[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] + Dxn[Dxt>0]) / Dxt[Dxt>0]
        AExn = np.roll(AExn, -1, axis = 1)
        
        AExnDec = self.zero()
        AExnDec[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0] + Dxn[DxDec>0]) / DxDec[DxDec>0]
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
        AExn2t[Dxt>0] = (Mxt[Dxt>0] - Mxn[Dxt>0] + Dxn[Dxt>0]) / Dxt[Dxt>0]
        AExn2t = np.roll(AExn2t, -1, axis = 1)
        
        AExnDec2t = self.zero()
        AExnDec2t[DxDec>0] = (MxDec[DxDec>0] - Mxn[DxDec>0] + Dxn[DxDec>0]) / DxDec[DxDec>0]
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
        
        mask10 = self.p['PMBMOD'] == 10
        mask2t = self.p['POLNBTETE'] == 2
        mask1t = self.p['POLNBTETE'] == 1
        
        self.AExn[mask1t | mask10] = AExn[mask1t | mask10]
        self.AExn[mask2t & (~mask10)] = AExn2t[mask2t & (~mask10)]
        
        
        self.axn[mask1t | mask10] = axn[mask1t | mask10]
        self.axn[mask2t & (~mask10)] = axn2t[mask2t & (~mask10)]


# Ne plus remonté à partir d'ici
# =============================================================================
# AJUSTEMENT DE VARIABLES
# =============================================================================


#Retourne la probabilité de décès d'expérience (FAUSSE DANS PROPHET POUR LES MODALITES 6 ET 7 CAR LA MORTALITE D'EXPERIENCE EST A 100%) A SUPPRIMER POUR CORRIGER !!
    def qxExp(self,assExp=1):
        
        mortExp = self.dc()
        # On ajuste la mortalité d'expérience pour modalité 6 et 7 (A SUPPRIMER POUR CORRIGER)
        mod = self.p['PMBMOD'].to_numpy()[:,np.newaxis,np.newaxis]  * self.one()
        mask = ((mod == 7) | (mod == 6))
        mortExp[mask] = 1
        myQx=self.qx(ass=assExp)*mortExp
        
        return np.copy(myQx)


#Retourne les taux de rachat selon le fractionnement. Les taux apparaissent uniquement le mois avant un paiement de prime (pas pour les mixtes) A SUPPRIMER POUR CORRIGER !!
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
        # frac=self.frac()
        frac=12*self.one()
        
        #Fractionnement à 0 sont remplacer par 1
        frac[frac==0]=12
        mylapse=1-(1-mylapse)**(1/frac)
        # mylapse= self.isLapse()*mylapse
        
        return mylapse


#Cette Loop renvoie l'ensemble des variables récusrives pour les produits épargnes
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
        
    # Modification les mixtes 2 tetes sont en fait calculée en fonction de l'assuré 1 (Ce qui est faux) (A MODIFIER) ?
        mask = (((self.p['PMBMOD']==2) & (self.p['POLNBTETE']==2))).astype(bool)
        qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
        qxy[mask] = 1-(1-qxy[mask])**(1/12)
        qxyD = lapseTiming * qxy

        # Variable actuarielle
        AExn = self.AExn

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
        axn = self.axn
        valSumAss = self.sumAss() * self.AExn
        provGestPP = self.provGestPP()
        pmFirstYear = self.pmFirstYear()    
        allocMonths = self.allocMonths()
        txPartPB = self.txPartPB()

        
        nbtete = self.p['POLNBTETE'][:,np.newaxis, np.newaxis]*self.one() 
        
        
        # Nouvelles variables
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
        tierPM = self.zero()
        zillTot = self.zero()
        pbSortMatsPP = self.zero()
        pbSortSurrPP = self.zero()
        pbSortDthPP = self.zero()
        

        # Calcul des PM au temps 0 
        valAccrbPP[:,0,:] = pbAcquPP[:,0,:] * AExn[:,0,:] 
        
        tierPM[:,0,:] = (1/3) * np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] + precPP[:,0,:] - valNetPP[:,0,:], 0)
            
        zillTot[:,0,:] = np.minimum(alpha[:,0,:] * prInventPP[:,0,:] * axn[:,0,:], np.maximum(valSumAss[:,0,:] - valNetPP[:,0,:] + provGestPP[:,0,:], 0))
            
        zill[:,0,:] = np.where((tierPM[:,0,:] <= zillTot[:,0,:]) & (nbtete[:,0,:] != 2), tierPM[:,0,:], zillTot[:,0,:])
        
        mathResPP[:,0,:] = np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] - valNetPP[:,0,:] + precPP[:,0,:] - zill[:,0,:], 0 )

        provTechPP[:,0,:] = mathResPP[:,0,:] - provGestPP[:,0,:] - precPP[:,0,:] + zill[:,0,:]
        
        pmZillPP[:,0,:] = provTechPP[:,0,:] - zill[:,0,:]
        
        
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
            
            tierPM[:,i,:] = (1/3) * (np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0))
            
            zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:], 0))
            
            zill[:,i,:] = np.where((tierPM[:,i,:] <= zillTot[:,i,:]) & (nbtete[:,i,:] != 2), tierPM[:,i,:], zillTot[:,i,:])
            
            mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )
            
            provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]
            
            pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
            pbSortSurrPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:] * AExn[:,i,:]
            
            pbSortDthPP[:,i,:] = pbCalcPP[:,i-1,:] * isActive[:,i,:]



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



# Sauvegarde des variables concernant les PM
 # Montant de PB à affecter par police
        self.pbCalcPP = pbCalcPP
  # PB acquise des polices actives
        self.pbAcquPP = pbAcquPP
# PB dfdonnée par police en cas de maturité     
        self.pbSortMatsPP = pbSortMatsPP
# PB donnée par police en cas de rachat
        self.pbSortSurrPP = pbSortSurrPP
# PM utilisée pour le calcul de la PB
        self.pmPourPB = pmPourPB
# PM Zillmérisée cumulée 
        self.pmZillCum = pmZillCum
# Provisions technique par police 
        self.provTechPP = provTechPP
# Reserves mathématiques par polices       
        self.mathResPP = mathResPP
# Valeur actualisée de la PB 
        self.valAccrbPP = valAccrbPP
# PB incorporée par polices       
        self.pbIncorPP = pbIncorPP
# Provision zillmérisée par police     
        self.pmZillPP = pmZillPP
# Zillmérisation 
        self.zill = zill
# Zillmérisation en comptant le (1/3) de la pm comme zill       
        self.zillTot = zillTot
# Tiers de la pm comptée comme zill       
        self.tierPM = tierPM
# PB donnée par police en cas de décès
        self.pbSortDthPP = pbSortDthPP



# Met un vecteur de 1 et 0 (1 si la police possède moins de 12 mois)
    def pmFirstYear(self):
        vec = self.one() * 12
        mask = self.durationIf() <= 12
        vec[mask] = self.durationIf()[mask]
        return vec
 
# Arrondi des tables afin d'obtenir taux pb (table rdt est). Le taux PB va également dépendre du taux d'intêret 
    def txPartPB(self):
        rate = (1+self.pbRate())**12 - 1
        rate = (1+rate)**(1/12) - 1

        # ligne à supprimer pour corriger !! il ne faut pas arrondir ce taux
        rate = np.round(rate, decimals = 6)
        
        txInt = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()/100
        return np.maximum(0, rate - txInt)
    
# =============================================================================
    ### CALCUL DES PREMIUMS
# =============================================================================

# Prime complémentaire qui va dépendre de la modalité et du tarif. Pourquoi POLPRCPLA est présent nulle part ici ?
    def annRider(self):
        
        # Prime complémentaire pour les mixtes
        primeCompl = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5']\
                      + self.p['POLPRCPL6'] + self.p['POLPRCPL9'])
            
        # Prime complémentaire pour les taux d'interet inférieur à 2.5 et age dépassant 65
        primeCompl2 = (self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL9'])
        
        # prime complémentaire pour les produits mixtes à 2 têtes (A SUPPRIMER POUR CORRIGER car il n'y a pas PA+ ici) !!
        mask22 = (self.p['POLNBTETE'] == 2)
        primeCompl[mask22] = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5'] + self.p['POLPRCPL6'])[mask22]   
        primeCompl2[mask22] = (self.p['POLPRCPL3'] + self.p['POLPRCPL4'])[mask22]
        
        # prime complémentaire pour pour les modalités 10
        mask10 = (self.p['PMBMOD'] == 10)
        primeCompl[mask10] = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5'] \
                              + self.p['POLPRCPL6'] + self.p['POLPRCPL8'] + self.p['POLPRCPL9'])[mask10]   
            
        primeCompl2[mask10] = primeCompl[mask10]
        primeCompl = primeCompl[:,np.newaxis,np.newaxis] * self.one()
        primeCompl2 = primeCompl2[:,np.newaxis,np.newaxis] * self.one()
        
        # Condition sur la limite d'age qui va dépendre de la modalité et du tarif, ici du taux t'intêret
        maskA = ((self.p['POLINTERG'] <= 2)[:,np.newaxis,np.newaxis] * self.one()).astype(bool)
        maskB = ((self.p['POLINTERG'] > 2)[:,np.newaxis,np.newaxis] * self.one()).astype(bool)
        
        maskCPL1 = (self.age() <= self.ageLimiteCPL1 ).astype(bool)
        maskCPL2 = (self.age() <= self.ageLimiteCPL2).astype(bool)
  
        total = self.zero()
        conditions = [ maskA * maskCPL1, maskA * maskCPL2, maskB * maskCPL1]
        choices = [primeCompl, primeCompl2, primeCompl]
        return np.select(conditions, choices, default=0)

#Retourne les primes totales perçues. Il faut prendre en compte les primes pouvant être indexé, et rajouté les autres primes sans indexation. POLPRCPLA pas dans ANNRIDER pourquoi ?
    def totalPremium(self):
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])/self.frac()
        premCompl = self.annRider() / self.frac()
        prem=(premInc*self.indexation() + premCompl) * self.nbrPolIfSM * self.isPremPay()
        # prime à 0 pour les modalités 6 et 7
        mask67 = self.mask([6,7])
        prem[mask67] = 0
        return prem


# =============================================================================
    ### CALCUL DES CLAIMS
# =============================================================================
# retourne la somme assurée avec le bon format
    def sumAss(self): 
        return self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one() 

# Calcul des primes d'inventaire annuelle (PA'')
    def prInventaire(self):
        loading = self.p['aquisitionLoading'][:,np.newaxis, np.newaxis]*self.one()   
        fraisFract = self.p['fraisFract'][:,np.newaxis, np.newaxis]*self.one()  
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])
        premInc = premInc * self.indexation()
        prInventaire = premInc * (1-loading) / fraisFract
        
        # Modalité 10 ont une prime d'inventaire de 0 (A SUPPRIMER POUR CORRIGER)
        mask = (self.p['POLSIT']==4) | (self.p['POLSIT']==9) | (self.p['PMBMOD'].isin([10])) 
        prInventaire[mask] = self.zero()[mask]
        return prInventaire
        
# Calcul des primes pures PR PURE PP
    def prPure(self):
        gestLoading = self.p['gestionLoadingSA'][:,np.newaxis, np.newaxis]*self.one() 
        capital = self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one()  
        prInvent = self.prInventaire()
        ppure = prInvent - gestLoading * capital
        mask = (self.p['POLSIT']==4) | (self.p['POLSIT']==9)
        ppure[mask] = self.zero()[mask]
        return ppure
        
# Valeur actualisée des primes nettes
    def valNetPrem(self):
        premNet = self.prPure()
        axn = self.axn
        valNetPrem = premNet * axn
        # mod6 et 7 valnetPrem = 0
        mask = self.p['PMBMOD'].isin([6,7])
        valNetPrem[mask] = self.zero()[mask]
        return valNetPrem

# Valeur actualisé SA (Net single premium value) AExn * capital
    def valSaPP(self):
        # mask ici car au moment de l'échéance de la police, le net Single premium = 0 et non Capital
        mask = self.polTermM() > self.durationIf() 
        valSaPP = self.zero()
        valSaPP[mask] = self.AExn[mask] * self.sumAss()[mask]
        return valSaPP

#Retourne les primes totales sans inforce ni fractionnement
    def annPremPP(self):
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])
        premInc=premInc*self.indexation()
        return premInc + self.annRider() 

#Retourne les provisions pour risque en cours. Reprendre une méthode commune à tout le portefeuille pour calculé les risque en cours !!
    def precPP(self):
        mask10 = self.mask([10])
        annPremPP = self.annPremPP()
    # pourquoi prend-on en compte les AnnRider pour les mod10 ?
        annPremPP[mask10] = self.annRider()[mask10]
        fraisFract = self.p['fraisFract'][:,np.newaxis, np.newaxis]*self.one() 
        loading = self.p['aquisitionLoading'][:,np.newaxis, np.newaxis]*self.one()  
        premForREC = annPremPP / fraisFract / (1+loading)
        precPP = premForREC * self.timeBeforeNextPay()/self.frac()
        
# calcul de precPP pour les modalité 10 (il faut une même méthode pour tout les risques en cours du portefeuille) !!
        frek=self.frac()
        premCompl = self.annRider()/frek 
        riderIncPP=premCompl*self.isPremPay()
        riderIncPP2=premCompl
        precPP10 = self.zero()
        
        for i in range(1,self.shape[1]):
            precPP10[:,i,:]=precPP10[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
        
        precPP[mask10] = precPP10[mask10]
        
        return precPP * self.isActive()

# retourne la provision mathèmatique de gestion
    def pmgSA(self):
        tauxPM =self.p['gestionLoadingSA'][:,np.newaxis, np.newaxis]*self.one()  
        return tauxPM * self.axn 

# Provision de gestion calculée sans pb
    def provGestPP(self):
        pm = self.pmgSA()  * self.sumAss() - self.axn * (self.prInventaire() - self.prPure())
        pm[self.p['PMBMOD'].isin([6,7])] = self.zero()[self.p['PMBMOD'].isin([6,7])]
        return pm


# claim complémentaire par police RIDER INC PP
    def riderIncPP(self):
        return (self.annRider() / self.frac()) * self.isPremPay()


# calcul du taux de sinistralité complémentaire
    def riderCRate(self):
        annRider = self.annRider()
        
        mask2 = ((self.p['PMBTXINT'] > 2)[:,np.newaxis, np.newaxis]*self.one()).astype(bool)
        mask0 = ((self.p['PMBTXINT'] <= 2)[:,np.newaxis, np.newaxis]*self.one()).astype(bool)
        maskCPL1 = (self.age() <= self.ageLimiteCPL1 ).astype(bool)
        maskCPL2 = (self.age() <= self.ageLimiteCPL2).astype(bool)
        
        primeIPT = self.p['POLPRCPL1'][:,np.newaxis, np.newaxis]*self.one() 
        primeTPLacc = self.p['POLPRCPL3'][:,np.newaxis, np.newaxis]*self.one() 
        primeExoIG = self.p['POLPRCPL4'][:,np.newaxis, np.newaxis]*self.one() 
        primeExoRenteIG = self.p['POLPRCPL5'][:,np.newaxis, np.newaxis]*self.one() 
        primeHospi = self.p['POLPRCPL6'][:,np.newaxis, np.newaxis]*self.one() 
        primeAccPA = self.p['POLPRCPL9'][:,np.newaxis, np.newaxis]*self.one() 
        primeDcAdulte = self.p['POLPRCPL8'][:,np.newaxis, np.newaxis]*self.one() 
        
        txIPT = self.ipt()
        txAcc = self.dcAccident()
        txExo = self.exo()
        txExoRenteIG = self.itt()
        txHospi = self.hospi()
        txAccPA = self.dcAccident()
        
        # taux jamais calculé, voici la correction
        # txDcAdulte = self.dcAccident() 
        txDcAdulte = self.one()
        
        tx = self.zero()
  
        cond1 = primeIPT * txIPT + primeTPLacc * txAcc + primeExoIG * txExo + primeExoRenteIG * txExoRenteIG + primeHospi * txHospi + primeAccPA * txAccPA
        cond2 = primeAccPA * txAccPA
        cond3 = primeTPLacc * txAcc + primeExoIG * txExo + primeAccPA * txAccPA

        conditions = [ mask2 & maskCPL1, mask2 & maskCPL2 , mask0 & maskCPL1, mask0 & maskCPL2]
        choices = [cond1, cond2, cond1, cond3]
        tx[annRider>0] = np.select(conditions, choices, default=0)[annRider>0] / annRider[annRider>0]
        
        # traitement modalité 10
        mask10 = self.p['PMBMOD'].isin([10])
        
        # ce taux est à 100 dans prophet A SUPPRIMER POUR CORRIGER
        txExoRenteIG[mask10] = self.one()[mask10]
        
        cond4 = primeExoIG * txExo + primeExoRenteIG * txExoRenteIG + primeDcAdulte * txDcAdulte
        tx[mask10] = cond4[mask10] / annRider[mask10]
        return tx

# Coût des complémentaires
    def riderCostPP(self): 
        return self.riderIncPP() * self.riderCRate()
     
 
# Calcul des claim complémentaire
    def claimCompl(self):
        maskPA = (self.p['POLPRCPLA'] != 0)
        maskNpa = (self.p['POLPRCPLA'] == 0)
        riderCoutgo = self.zero()
        riderCoutgo[maskPA] = self.riderCostPP()[maskPA] * self.nbrPolIfSM[maskPA] + self.nbrDeath[maskPA] * self.capPA()[maskPA]
        riderCoutgo[maskNpa] = self.riderCostPP()[maskNpa] * self.nbrPolIfSM[maskNpa] 
        return riderCoutgo
    
    
# calcul des benefices en cas de maturité par police
    def matBenPP(self):
        return self.pbAcquPP + self.sumAss() + self.pbSortMatsPP
    
 # calcul des sorties total en cas de maturité 
    def maturity(self):
        noMats = self.nbrNewMat
        matBenPP = self.matBenPP()
        matOutgo = self.zero()

        for i in range(1,self.shape[1]):
            matOutgo[:,i,:] = matBenPP[:,i-1,:] * noMats[:,i,:] 
        
        return matOutgo
    
    
# calcul de la valeur en cas de lapse
    def surrValPP(self):
        pb = self.pbSortSurrPP
        pm = self.mathResPP
        surrValue = self.zero()
        # le rachat n'est possible qu'après 3 ans
        surrValue[self.durationIf() > 36] = np.maximum(pm, pb)[self.durationIf() > 36]
        # Calcul des surrender outgo pour les modalité 6 et 7. Pourquoi la valeur change pour ces modalité ?
        pmzill = self.pmZillPP
        surrValue[self.mask([6,7])] = pmzill[self.mask([6,7])]
        return surrValue
    
    
# calcul des sorties en cas de rachat
    def surrender(self):
        return self.surrValPP() * self.nbrSurrender
    
# retourne un vecteur de 1 à 12 selon la duration de la police, si + élevé de 12 mois alors 12
    def firstYear(self):
        dur = self.durationIf()
        dur[dur>12] = 12 
        return dur

#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        return (self.sumAss() + self.pbAcquPP) * self.nbrDeath



# =============================================================================
    ### CALCUL DES EXPENSES
# =============================================================================

# calcul des reserves par police
    def mathResBA(self):
        return np.maximum(self.valSaPP() + self.valAccrbPP + self.provGestPP() + self.precPP() - self.valNetPrem() - self.zill, 0) 

# reserves inforce
    def provMathIf(self):
        return self.mathResPP * self.nbrPolIf
    

# Dotation PB inforce actualisé
    def dotationPB(self):
        return self.pbCalcPP * self.AExn * self.nbrPolIf

# Calcul de l'évolution du fond de PB
    def fondPB(self):
        dotationPB = self.dotationPB()
        fondPB = self.zero()
        reprisePB = self.zero()
 
        for i in range(1,self.shape[1]):
            reprisePB[:,i,:] = fondPB[:,i-1,:]
            fondPB[:,i,:] =  fondPB[:,i-1,:] + dotationPB[:,i,:] - reprisePB[:,i,:]
        return fondPB
    
# Reprise pour incorporation de PB
    def reprisePB(self):
        return np.roll(self.fondPB(), 1, axis = 1)
    
# Reprise sur fond de PB suite à une maturité  
    def repPbMats(self):
        return self.zero()
    
# pb incorporée actualisé inforce
    def pbIncorpIF(self):
        AExn = np.roll(self.AExn, 1, axis = 1)
        return self.pbIncorPP * AExn * self.nbrPolIfSM
    
    
# coût de la pb sur sorties
    def pbSortie(self):
        pbSortMatsPP = np.roll(self.pbSortMatsPP, 1, axis = 1)
        # A mon avis pbSortSurr et pbSortDth ne devraient pas être à 0, ce sont les pb donnée en cas de sortie pour décès ou lapse (?) 
        pbSortSurrPP = self.zero()
        pbSortDthPP = self.zero()
        valueLapse = pbSortDthPP * self.nbrDeath + pbSortSurrPP * self.nbrSurrender + pbSortMatsPP * self.nbrNewMat
        value = pbSortDthPP * self.nbrDeath + pbSortMatsPP * self.nbrNewMat
        value[self.surrValPP() > 0] = valueLapse[self.surrValPP() > 0]
        return value
    
# Zillmérisation inforce
    def valZillIf(self):
        return  self.zill * self.nbrPolIf
    
# calcul des provisions techniques en cours, inforce
    def provTechIf(self):
        return self.provTechPP * self.nbrPolIf 
    
# diminution de la provision non zilmérisée à la maturité du contrat 
    def tresRldMat(self):
        return np.roll(self.provTechPP, 1, axis = 1) * self.nbrNewMat
     
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
    
    
# provision de gestion en cours 
    def provGestIf(self):
        return self.provGestPP() * self.nbrPolIf


  # calcul des intêret techniques crédités (INT_CRED_T) 
    def totIntCred(self):
        
# intêrets techniques crédité        
        intCredT = (self.txInt()-1) * self.provTechAj()
        intCredT[:,0,:] = 0
        
# intêrets crédités sur provision de gestion en cours
        intCredPMG = np.roll(self.provGestIf(), 1, axis = 1) * (self.txInt()-1)
        
# Intêrets crédités sur zillmérisation     
        intCredZil = (self.txInt()-1) * np.roll(self.valZillIf(), 1, axis = 1)
        intCredZil[:,0,:] = 0
        
        return intCredT + intCredPMG - intCredZil
    
    
# Arrondi des tables ACTU.FAC afin d'obtenir mUfii (table rdt est)
# méthode suivante à supprimer, il n'y a aucune raison d'arrondir le taux d'intêret !!
    def mUfii(self):
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        rate = (1+rate)**(1/12) - 1
        return rate
 # A remplacer par:
     # def mUfii(self):
     #    return self.rate()
# Ou changer le nom des mUfii par self.rate()



# # loop pour calculer les reserves pour expense ADJ_MATHRES2
    def reserveForExp(self):
        
          # déclaration des nouvelles variables
          resReldMat = self.zero()
          totExp = self.zero()
          rfinAnn = self.zero()
          oTaxblInc = self.zero()
          adjMathRes2 = self.zero()
          resFinMois = self.zero()
          provMathAj = self.zero()
        
          # Nombre polices
          nbrPolIf = self.nbrPolIf
          noMat = self.nbrNewMat
 
          # fonction existantes
          fMathResIF = self.provMathIf() + self.fondPB()
          provMathIf = self.provMathIf()
          riderCoutgo = self.claimCompl()
          pbIncorpIF = self.pbIncorpIF()
          premInc = self.totalPremium()

          fondPB = self.fondPB()
          mUfii = self.mUfii()
          repPbMats = self.repPbMats()
          premInvest = self.prPure() * self.nbrPolIfSM * self.isPremPay() / self.frac()
          # les primes investies sont à 0 pour les modalité à primes unique
          premInvest[self.p['PMBMOD'].isin([6,7])] = self.zero()[self.p['PMBMOD'].isin([6,7])]
          unitExp = self.unitExpense()
          reprisePB = self.reprisePB()
          dotationPB = self.dotationPB()
          pbSortie = self.pbSortie()
          totIntCred = self.totIntCred() 
          txReserve = self.fraisGestionPlacement()
          mathresPP = self.mathResPP  
          totComm = self.totalCommissions()
          monthPb = self.one() - self.allocMonths()
          isActive = self.isActive()
      
          for i in range(1,self.shape[1]):
            
              resReldMatTEMP =  (fondPB[:,i-1,:] + rfinAnn[:,i-1,:])
            
              resReldMat[:,i,:] = np.divide(resReldMatTEMP, (nbrPolIf[:,i-1,:]), out=np.zeros_like(resReldMatTEMP), where=(nbrPolIf[:,i-1,:])!=0)\
                  * noMat[:,i,:] + mathresPP[:,i-1,:] * noMat[:,i,:] 
            
              adjMathRes2[:,i,:] = fMathResIF[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:] - resReldMat[:,i,:] - repPbMats[:,i,:]
        
              totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
                
              provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + pbIncorpIF[:,i,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - (totExp[:,i,:] + totComm[:,i,:]) - resReldMat[:,i,:]
        
              oTaxblInc[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            
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


# =============================================================================
# --- DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES
# =============================================================================


pol = MI()
#pol=MI(run=[4,5])


    ###  Mod 2_1 produit F1XT1
# pol.ids([301])

# pol.ids([106903])
# pol.ids([301])

# pol.ids([47906])

# pol.modHead([2],1)

    ### Mod 2_2 F2XT_1
# pol.ids([1019201])

# pol.ids([2142901])
# pol.modHead([2],2)

    ### Mod 10 F1XT14
# pol.ids([2078101])

# pol.ids([2078101])
# pol.mod([10])

    ### Mod 6 F1XT11
# pol.ids([1637205])
# pol.mod([6,7])
# 
# mod7
# pol.ids([101])

# age = pol.age()

# pol.mod([6,7,2,10])
# check = pol.PGG() 
# pureprem = pol.purePremium()

# a = pol.p
# b=pol.oTaxblInc
# check = pol.Lxx(pol.age())
# c=pol.nbrPolIfSM
# d=pol.nbrNewMat
# e=pol.nbrDeath
# f=pol.nbrSurrender
# g=pol.premiumCompl()
#h=pol.premiumPure()
#i=pol.deathClaim()
#j=pol.fraisVisiteClaim()
#k=pol.timeBeforeNextPay()
#l=pol.risqueEnCour()
# m=pol.adjustedReserve()
#n=pol.reserveExpense()
#o=pol.unitExpense()
# p=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()

# bel=np.sum(pol.BEL(), axis=0)
# pgg=pol.PGG()

# a=pol.p.groupby('ClassPGG').sum()
# a=a['PMbasePGG']

print("Class MI--- %s sec" %'%.2f'%  (time.time() - start_time))

# monCas=check
# zz=np.sum(monCas, axis=0)
# zzz=np.sum(zz[:,0])
# z=pd.DataFrame(monCas[:,:,0])
# z=z.sum()
# z.to_csv(path+'/zJO/check.csv',header=False)


# aaa=aa[['PMBPOL', 'PMBFRACT','POLSIT','PMBMOD','PMBTXINT']]

# AExmTEST = pol.AExn(pol.age(), GKM95)

# pol.p.to_excel(path+'/zJO/check portefeuille.xlsx', header = True )
# aa.to_excel("check portefeuille.xlsx", header = True )


#Visualiser une dimension d'un numpy qui n'apparait pas
#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])
# AExn = pol.AExn()




# Mask35 =pol.p['ClassPGG'] == 'MI3.5'
# pm35 = pol.p.loc[Mask35, 'PMbasePGG']

# Mask25 =pol.p['ClassPGG'] == 'MI2.5'
# pm25 = pol.p.loc[Mask25, 'PMbasePGG']

# Mask20 =pol.p['ClassPGG'] == 'MI2.0'
# pm20 = pol.p.loc[Mask20, 'PMbasePGG']

# Mask10 =pol.p['ClassPGG'] == 'MI1.0'
# pm10 = pol.p.loc[Mask10, 'PMbasePGG']

# Mask175 =pol.p['ClassPGG'] == 'MI1.75'
# pm175 = pol.p.loc[Mask175, 'PMbasePGG']

# Mask125 =pol.p['ClassPGG'] == 'MI1.25'
# pm125 = pol.p.loc[Mask125, 'PMbasePGG']


# Mask075 =pol.p['ClassPGG'] == 'MI0.75'
# pm075 = pol.p.loc[Mask075, 'PMbasePGG']

# Mask05 =pol.p['ClassPGG'] == 'MI0.5'
# pm05 = pol.p.loc[Mask05, 'PMbasePGG']

# Mask025 =pol.p['ClassPGG'] == 'MI0.25'
# pm025 = pol.p.loc[Mask025, 'PMbasePGG']

# Mask0 =pol.p['ClassPGG'] == 'MI0.0'
# pm0 = pol.p.loc[Mask0, 'PMbasePGG']




# sum(pm0)
# sum(pm025)
# sum(pm05)
# sum(pm075)
# sum(pm10)
# sum(pm20)
# sum(pm25)
# sum(pm35)
# sum(pm125)
# sum(pm175)


# sum(pm0)+sum(pm025)+sum(pm05)+sum(pm075)+sum(pm10)+sum(pm20)+sum(pm25)+sum(pm35)+sum(pm125)+sum(pm175)




# sum(pmtot)

