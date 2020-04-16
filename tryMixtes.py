from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
from MyPyliferisk import Actuarial
from MyPyliferisk.mortalitytables import *
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()


# =============================================================================
# Création de la class Epargne
# =============================================================================

class MI(Portfolio):
    # mods=[2,10,6,7]
    # mods=[10]

#Products: F1XT_1,F2XT_1,F1XT14,F1XT11
    
    # age limite pour la garantie complémentaire CPL1
    ageLimiteCPL1 = 60
    ageLimiteCPL2 = 65
    tableHommes = EKM1995
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        # self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.commutations()
        self.loopSaving()


# # Fonction présent dans l'update permettant de chargé une fois tous les symboles de commutation
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
        
        self.AExn[self.p['POLNBTETE']==1] = AExn[self.p['POLNBTETE']==1]
        self.AExn[self.p['POLNBTETE']==2] = AExn2t[self.p['POLNBTETE']==2]
        
        
        self.axn[self.p['POLNBTETE']==1] = axn[self.p['POLNBTETE']==1]
        self.axn[self.p['POLNBTETE']==2] = axn2t[self.p['POLNBTETE']==2]


#Retourne la probabilité de décès d'expérience (FAUSSE DANS PROPHET POUR LES MODALITES 6 ET 7 CAR LA MORTALITE D'EXPERIENCE EST A 100%)
    def qxExp(self,assExp=1):
        
        mortExp = self.dc()
        # On ajuste la mortalité d'expérience pour modalité 6 et 7 (A SUPPRIMER POUR CORRIGER)
        mod = self.p['PMBMOD'].to_numpy()[:,np.newaxis,np.newaxis]  * self.one()
        mask = ((mod == 7) | (mod == 6))
        mortExp[mask] = 1
        myQx=self.qx(ass=assExp)*mortExp
        
        return np.copy(myQx)


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
        # frac=self.frac()
        frac=12*self.one()
        
        #Fractionnement à 0 sont remplacer par 1
        frac[frac==0]=12
        mylapse=1-(1-mylapse)**(1/frac)
        
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
        reduction = self.reduction()    
        qxy = self.qxExpMens() 
        qx = self.qxExp()
        
    # Modification les mixtes 2 tetes sont en fait calculée en fonction de l'assuré 1 (Ce qui est faux) (A MODIFIER)
        mask = (((self.p['PMBMOD']==2) & (self.p['POLNBTETE']==2))).astype(bool)
        qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
        qxy[mask] = 1-(1-qxy[mask])**(1/12)
        qxyD = lapseTiming * qxy
        txInteret = self.txInt()

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
        

        # Calcul des PM au temps 0 
        valAccrbPP[:,0,:] = pbAcquPP[:,0,:] * AExn[:,0,:] 
        
        tierPM[:,0,:] = (1/3) * np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] + precPP[:,0,:] - valNetPP[:,0,:], 0)
            
        zillTot[:,0,:] = np.minimum(alpha[:,0,:] * prInventPP[:,0,:] * axn[:,0,:], np.maximum(valSumAss[:,0,:] - valNetPP[:,0,:] + provGestPP[:,0,:], 0))
            
        zill[:,0,:] = np.where(tierPM[:,0,:] <= zillTot[:,0,:], tierPM[:,0,:], zillTot[:,0,:])
        
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


# Variable permettant le calcul des reserves

            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

            valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] 
            
            tierPM[:,i,:] = (1/3) * (np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0))
            
            zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:], 0))
            
            
            zill[:,i,:] = np.where(tierPM[:,i,:] <= zillTot[:,i,:], tierPM[:,i,:], zillTot[:,i,:])
            
          
            
            mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )

            provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]



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


        self.pmPourPB = pmPourPB
        self.pmZillCum = pmZillCum
        self.provTechPP = provTechPP
        self.mathResPP = mathResPP
        self.valAccrbPP = valAccrbPP
        self.pbIncorPP = pbIncorPP
        self.pmZillPP = pmZillPP
        self.valAccrbPP = valAccrbPP
        self.zill = zill
        self.zillTot = zillTot
        self.tierPM = tierPM

# Vecteur de 1 et 0 permettant de savoir si police toujours active ou non
    def isActive(self):
        
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask

# Met un vecteur de 1 et 0 (1 si la police possède moins de 12 mois)
    def pmFirstYear(self):
        vec = self.one() * 12
        mask = self.durationIf() <= 12
        vec[mask] = self.durationIf()[mask]
        return vec

# Retourne un vecteur de 1 et 0, Met des 1 pour le mois de janvier (là ou la PB est versée)
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth ==1
        return mask*1
    
 
# Arrondi des tables afin d'obtenir taux pb (table rdt est). Le taux va également dépendre du taux d'intêret
    def txPartPB(self):
        rate = (1+self.pbRate())**12 - 1
        rate = (1+rate)**(1/12) - 1
        rate = np.round(rate, decimals = 6)
        txInt = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()/100
        rate = np.maximum(0, rate - txInt)
        return rate
    
# =============================================================================
    ### FONCTIONS ACTUARIELLES
# =============================================================================       
 
# Age au début de la police 
    def ageInit(self):
        age = (self.p['Age1AtEntry'].to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age

# Age à la fin du contrat
    def ageFinal(self):
        age = ((self.p['Age1AtEntry'] + (self.p['residualTermM'] + self.p['DurationIfInitial'])/12).to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age
     
# age à la fin du paiement des primes 
    def agePrimes(self):
        age = ((self.p['Age1AtEntry'].to_numpy() + self.p['POLDURP'].to_numpy())[:,np.newaxis,np.newaxis]*self.one())
        return age

    
 # Fonction générique actuarielle
    def actu(self, var, x, nbtetes = 1):
        
        table = self.p['POLTBMORT'].unique()
        tbMort = self.p['POLTBMORT']
               
        if x == 'x':
            myAge = self.ageInit().astype(int)
        elif x == 't':
            myAge = self.age().astype(int) 
        elif x == 't+1':
            myAge = self.age().astype(int) + 1
        elif x == 'n':
            myAge = self.ageFinal().astype(int) 
        elif x == 'p':
            myAge = self.agePrimes().astype(int)
       
        txTech = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis] / 100
        txTechLoop = np.unique(self.p['PMBTXINT'].to_numpy())
        tbMort = tbMort[:,np.newaxis,np.newaxis]
        myVarx = self.zero()
        one = self.one()
        zero = self.zero()
        
        for tb in table:
            mask_tableMort = ((tbMort == tb)*one).astype(bool)
            for i in np.nditer(txTechLoop):
                txInt = i / 100
                mask_txTech = ((txTech == txInt)*one).astype(bool)
                mt = Actuarial(nt=eval(tb), i=txInt, nbtete = nbtetes)
                aVARx = pd.DataFrame(getattr(mt, var)).to_numpy()
                myAge2 = np.where(myAge>=mt.w, mt.w, myAge)
                myVarx[mask_txTech & mask_tableMort] = np.take(aVARx, myAge2[mask_txTech & mask_tableMort])
                myVarx[mask_txTech & mask_tableMort & (myAge>mt.w)] = zero[mask_txTech & mask_tableMort & (myAge>mt.w)]
        return myVarx    






# Créer un vecteur permettant d'interpolé les vecteur en fonction de la date début de la police
    def interp(self, var, varDec):
        dur = self.durationIf()
        interp = np.int16(dur/12) + 1-(dur/12)
        resultat = (var * interp) + ((1-interp) * varDec)
        return resultat * self.isActive()
    
# =============================================================================
# --- CALCUL DES PREMIUMS
# =============================================================================

# Prime complémentaire qui va dépendre de la modalité et du tarif
    def annRider(self):
        
        # Prime complémentaire pour les mixtes
        primeCompl = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5']\
                      + self.p['POLPRCPL6'] + self.p['POLPRCPL9'])
            
        # Prime complémentaire pour les taux d'interet inférieur à 2.5 et age dépassant 65
        primeCompl2 = (self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL9'])
        
        # prime complémentaire pour les produits mixtes à 2 têtes (A SUPPRIMER POUR CORRIGER)
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
        conditions = [ maskA * maskCPL1, maskA * maskCPL2, maskB * maskCPL1  ]
        choices = [ primeCompl, primeCompl2, primeCompl]
        total = np.select(conditions, choices, default=0)
       
        return total

#Retourne les primes totales perçues
    def totalPremium(self):
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])/self.frac()
        premCompl = self.annRider() / self.frac()
        prem=(premInc*self.indexation() + premCompl) * self.nbrPolIfSM * self.isPremPay()
        # prime à 0 pour les modalités 6 et 7
        mask67 = self.mask([6,7])
        prem[mask67] = 0
        return prem

# =============================================================================
# --- CALCUL DES CLAIMS
# =============================================================================

# retourne la somme assurée avec le bon format
    def sumAss(self):
        sumAss = self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one()   
        return sumAss

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
        
        # mod7 valnetPrem = 0
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
        premCompl = self.annRider() 
        return premInc + premCompl

#Retourne les provisions pour risque en cours
    def precPP(self):
        annPremPP = self.annPremPP()
        fraisFract = self.p['fraisFract'][:,np.newaxis, np.newaxis]*self.one() 
        loading = self.p['aquisitionLoading'][:,np.newaxis, np.newaxis]*self.one()  
        premForREC = annPremPP / fraisFract / (1+loading)
        precPP = premForREC * self.timeBeforeNextPay()/self.frac()
        return precPP * self.isActive()

# retourne la provision mathèmatique de gestion
    def pmgSA(self):
        tauxPM =self.p['gestionLoadingSA'][:,np.newaxis, np.newaxis]*self.one()  
        valPolFac = self.axn
        pm = tauxPM * valPolFac 
        return pm

# Provision de gestion calculée sans pb
    def provGestPP(self):
        pm = self.pmgSA()  * self.sumAss() - self.axn * (self.prInventaire() - self.prPure())
        return pm

# provision de gestion Inforce (INFORMATIF)
    def provGestIF(self):
        pmIF = self.provGestPP() * self.nbrPolIf
        return pmIF
    
# Pb acquise in force (INFORMATIF)
    def pbAcqIF(self):
        pb = self.pbAcquPP * self.nbrPolIf
        return pb


# claim complémentaire par police RIDER INC PP
    def riderIncPP(self):
        riderIncPP = self.annRider() / self.frac()
        riderIncPP = riderIncPP * self.isPremPay()
        return riderIncPP


# recalcul du taux DC accident pour : (je cite) tenir en compte la sinistralité de la garantie décès de l'epargne en fonction du qx - 26.01.2015
    def dcAccidentAdjusted(self):
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
        
        txIPT = self.ipt()
        txAcc = self.dcAccident()
        txExo = self.exo()
        txExoRenteIG = self.itt()
        txHospi = self.hospi()
        txAccPA = self.dcAccident()
        
        tx = self.zero()
  
        cond1 = primeIPT * txIPT + primeTPLacc * txAcc + primeExoIG * txExo + primeExoRenteIG * txExoRenteIG + primeHospi * txHospi + primeAccPA * txAccPA
        cond2 = primeAccPA * txAccPA
        cond3 = primeTPLacc * txAcc + primeExoIG * txExo + primeAccPA * txAccPA

        conditions = [ mask2 & maskCPL1, mask2 & maskCPL2 , mask0 & maskCPL1, mask0 & maskCPL2]
        choices = [cond1, cond2, cond1, cond3]
        tx[annRider>0] = np.select(conditions, choices, default=0)[annRider>0] / annRider[annRider>0]
        return tx


    def riderCostPP(self):
        riderCostPP = self.riderIncPP() * self.dcAccidentAdjusted()
        return riderCostPP
    
    
 # ici on détermine le capital pour Protection d'avenir en fonction de l'âge
    def capPA(self):
        
        capPA = self.zero()
        capPA[self.age() <= 55]= 25000
        capPA[(self.age() > 55)]= 5000
        capPA[self.age() > 65]= 0
        capPA[self.p['POLPRCPL9'] == 0]=0
        return capPA
    
 
# Calcul des claim complémentaire
    def claimCompl(self):
        maskPA = (self.p['POLPRCPLA'] != 0)
        maskNpa = (self.p['POLPRCPLA'] == 0)
        
        riderCoutgo = self.zero()
        riderCoutgo[maskPA] = self.riderCostPP()[maskPA] * self.nbrPolIfSM[maskPA] + self.nbrDeath[maskPA] * self.capPA()[maskPA]
        riderCoutgo[maskNpa] = self.riderCostPP()[maskNpa] * self.nbrPolIfSM[maskNpa] 
        return riderCoutgo

# # loop pour calculer les reserves
#     def reserve(self):
        
        
#         # Variable existante
#         zill = self.zero()
#         precPP = self.precPP()
#         valSaPP = self.valSaPP()
#         valNetPP = self.valNetPrem()
#         AExn = self.AExn()
#         prInventPP = self.prInventaire()
#         alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
#         axn = self.axn()
#         valSumAss = self.sumAss() * self.AExn()
#         provGestPP = self.provGestPP()
        
        
#         # Nouvelles variables
#         valAccrbPP = self.zero()
#         pbIncorPP = self.zero()
#         pbAcquPP = self.zero()
#         pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
#         pbCalcPP = self.zero()
#         isActive = self.isActive()
#         mathResPP = self.zero()
       
#         provTechPP = self.zero()
#         pmZillCum = self.zero()
#         pmZillPP = self.zero()
#         pmPourPB = self.zero()
#         tierPM = self.zero()
#         zillTot = self.zero()
        
        
#         #Variables de l'épargne actifs et réduits
#         epargnAcquPP = self.zero()        
#         eppAcquAPPUP = self.zero()
#         epAcquAVPUP = self.zero()

#         epargnAcquPP[:,0,:] = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]        

# #Variables de PB actifs et réduites

#         pbAcquAVPUP = self.zero()
#         pbAcquAPPUP = self.zero()
#         pbIncorPUP = self.zero()      
#         epgTxPbPUP = self.zero()
#         pbCalcPUP = self.zero()
#         pbPupDTHS = self.zero()
#         pbSortDTHS = self.zero()
        
#         epgTxPbPUP[:,0,:] = 0
        
#         pbSortMatsPP= self.zero()
#         pbSortMatsPUP = self.zero()
#         allocMonths = self.allocMonths()
        
#         # Variable existante
#         pmFirstYear = self.pmFirstYear()
    
   
#         # Taux annualisé
#         txIntPC = self.txInt()**(12) - 1
#         # txPbPC = self.txPbPC()/100
        
#         # taux annualisé
#         txIntPC = self.txInt()**(12) - 1
#         txPartPB = self.txPartPB()
        
#         # txTot = 1 + (txPbPC + txIntPC)
        

        
        
#         pbCalcPPdths = self.zero()
#         pbCalcPUPdths = self.zero()
        
     
#         # nouvelles variables
#         pmPourPB = self.zero()
        
        
        
#         # Calcul au temps 0
#         tierPM[:,0,:] = (1/3) * np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] + precPP[:,0,:] - valNetPP[:,0,:], 0)
            
#         zillTot[:,0,:] = np.minimum(alpha[:,0,:] * prInventPP[:,0,:] * axn[:,0,:], np.maximum(valSumAss[:,0,:] - valNetPP[:,0,:] + provGestPP[:,0,:], 0))
            
            
#         zill[:,0,:] = np.where(tierPM[:,0,:] <= zillTot[:,0,:], tierPM[:,0,:], zillTot[:,0,:])
        
#         mathResPP[:,0,:] = np.maximum(valSaPP[:,0,:] + valAccrbPP[:,0,:] + provGestPP[:,0,:] - valNetPP[:,0,:] + precPP[:,0,:] - zill[:,0,:], 0 )

#         provTechPP[:,0,:] = mathResPP[:,0,:] - provGestPP[:,0,:] - precPP[:,0,:] + zill[:,0,:]
        
#         pmZillPP[:,0,:] = provTechPP[:,0,:] - zill[:,0,:]
        
        
#         for i in range(1,self.shape[1]):
        
        
        
#         # #Définition des variables d'épargne pour actives et réduites
# #             epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]

# #             epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
# #             epTemp = epAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + epargnAcquPP[:,i,:] * nbrNewRed[:,i,:]
            
# #             eppAcquAPPUP[:,i,:] = np.divide(epTemp,nbrPupsIf[:,i,:],out=np.zeros_like(epTemp), where=nbrPupsIf[:,i,:]!=0)

            
# # # #Définition des variables de PB pour actives et réduites  
    
            
# #             pbIncorPUP[:,i,:] = np.nan_to_num(pbCalcPUP[:,i-1,:]  * isActive[:,i-1,:]) 
            
# #             pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:]) * txInteret[:,i,:] * isActive[:,i,:] 


#             pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
#             pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

#             valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] 
            
#             tierPM[:,i,:] = (1/3) * (np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0))
            
#             zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:] + provGestPP[:,i,:], 0))
            
            
#             zill[:,i,:] = np.where(tierPM[:,i,:] <= zillTot[:,i,:], tierPM[:,i,:], zillTot[:,i,:])
            
          
            
#             mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + provGestPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )

#             provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
#             pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
#             pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            
#             pmPourPB[:,i,:] = (pmZillCum[:,i,:] / 12) * allocMonths[:,i,:]
            
            
#             pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
#             pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]
            
            
         

# #             pbSortDTHS[:,i,:] = np.nan_to_num(pbCalcPPdths[:,i,:] * isActive[:,i,:]) 
            
# #             pbPupDTHS[:,i,:] = np.nan_to_num(pbCalcPUPdths[:,i,:] * isActive[:,i,:]) 
         
# #             pbAcquAVPUP[:,i,:] = (pbAcquAPPUP[:,i-1,:] + pbIncorPUP[:,i,:]) * txInteret[:,i,:]

     

# #             pbTemp=pbAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + pbAcquPP[:,i,:] * nbrNewRed[:,i,:]            
            
# #             pbAcquAPPUP[:,i,:] = np.divide(pbTemp,nbrPupsIf[:,i,:],out=np.zeros_like(pbTemp), where=nbrPupsIf[:,i,:]!=0)       
  
# #             epgTxTEMP = epgTxPbPUP[:,i-1,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) * (txTot[:,i,:]**(1/12)) + (epgTxPB_PP[:,i,:] *  nbrNewRed[:,i,:])
            
# #             epgTxPbPUP[:,i,:] =  np.divide(epgTxTEMP, nbrPupsIf[:,i,:], out=np.zeros_like(epgTxTEMP), where=nbrPupsIf[:,i,:]!=0)
            
            
            
             
            
# #             pbCalcPUP[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * allocMonths[:,i,:]
            
# #             pbCalcPPdths[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
# #             pbCalcPUPdths[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
# #             pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
# #             pbSortMatsPUP[:,i,:] = pbCalcPUP[:,i,:] * isActive[:,i,:]





# # #Sauvegarde des variables d'éparnge actifs et réduites
        
# #         #Epargne acquise par police AVANT nouvelle réduction                                 
# #         self.epAcquAVPUP=epAcquAVPUP
# #         #Epargne acquise par police APRES nouvelle réduction 
# #         self.eppAcquAPPUP=eppAcquAPPUP
# #         #Epargne aquise des polices actives
# #         self.epargnAcquPP = epargnAcquPP



# # #Sauvgarde des variables de  PB pour actives et réduites
        
# #         # PB acquise par police AVANT nouvelle réduction                                 
# #         self.pbAcquAVPUP=np.nan_to_num(pbAcquAVPUP)
# #         # PB acquise par police APRES nouvelle réduction 
# #         self.pbAcquAPPUP=np.nan_to_num(pbAcquAPPUP)
# #         #  PB à affecter par police réduite
# #         self.pbCalcPUP = pbCalcPUP
# #         # epargne et PB des polices réduites calculé au taux PB
# #         self.epgTxPbPUP = epgTxPbPUP
# #         # PB incorporée par contrat réduit
# #         self.pbIncorPUP = pbIncorPUP
# #         # Montant de PB à affecter par police
#         self.pbCalcPP = pbCalcPP
# #         # PB acquise des polices actives
#         self.pbAcquPP = pbAcquPP
# #         # PB incorporée par police
# #         self.pbIncorPP = pbIncorPP
# #         # PB incorporée par police réduite
# #         self.pbIncorPUP = pbIncorPUP
# #         # PB non incorporée des polices réduites
# #         self.pbPupDTHS=pbPupDTHS
# #         # PB non incorporée des polices actives
# #         self.pbSortDTHS=pbSortDTHS
# #         # Pb donnée par police en cas de maturité
# #         self.pbSortMatsPP = pbSortMatsPP
# #         # pb donnée par police en cas de maturité d'une police réduite
# #         self.pbSortMatsPUP = pbSortMatsPUP     
# #         # pb donnée par police en cas de décès
# #         self.pbCalcPPdths = pbCalcPPdths
# #         # pb donné par police en cas de décès d'une police réduite
# #         self.pbCalcPUPdths = pbCalcPUPdths
        






#         # self.pmPourPB = pmPourPB
#         # self.pmZillCum = pmZillCum
#         # self.provTechPP = provTechPP
#         # self.mathResPP = mathResPP
#         # self.valAccrbPP = valAccrbPP
#         # self.pbIncorPP = pbIncorPP
#         # self.pmZillPP = pmZillPP
#         # self.valAccrbPP = valAccrbPP
#         # self.zill = zill
        
#         # self.zillTot = zillTot
#         # self.tierPM = tierPM


# retourne un vecteur de 1 à 12 selon la duration de la police, si + élevé de 12 mois alors 12
    def firstYear(self):
        dur = self.durationIf()
        dur[dur>12] = 12 
        return dur

#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        deathBenPP = self.sumAss() + self.pbAcquPP
        deathOutgo = deathBenPP * self.nbrDeath
        return deathOutgo



#Retourne les rachats totaux (SURR_OUTGO)
    def surrender(self):
        return self.zero()

#Retourne les rachats partiels (PARTSV_OUTGO)
    def partialSurrender(self):
        return self.zero()

#Retourne les échéances (MAT_OUTGO)
    def maturity(self):
        return self.zero()


# =============================================================================
# --- CALCUL DES EXPENSES
# =============================================================================

#Retourne le coût par police pour les polices avec réduction possible (RENEXP_XRSE)
    def unitExpense(self):
        
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        
        coutParPolice=self.fraisGestion()

        cost=coutParPolice*inflation*(self.nbrPolIfSM + self.nbrPupIfSM)
        
        return cost



# =============================================================================
# --- DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES
# =============================================================================


def tester(self):
    return self

pol = MI()
#pol=MI(run=[4,5])

    ###  Mod 2_1 produit F1XT1
# pol.ids([301])

# pol.ids([106907])
# pol.ids([301])

# pol.ids([829603])

# pol.modHead([2],1)

    ### Mod 2_2 F2XT_1
# pol.ids([22101])
# pol.modHead([2],2)

    ### Mod 10 F1XT14
# pol.ids([1602604])
pol.mod([10])

    ### Mod 6 F1XT11
# pol.ids([799003])
# pol.mod([6,7])

# mod7
# pol.ids([101])

# age = pol.age()


check = pol.claimCompl()
# pureprem = pol.purePremium()

# a = pol.p
b=pol.pbAcqIF()
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
p=pol.totalPremium()
# q=pol.totalClaim()
# r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()

# bel=np.sum(pol.BEL(), axis=0)
# pgg=pol.PGG()



print("Class MI--- %s sec" %'%.2f'%  (time.time() - start_time))

monCas=check
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zJO/check.csv',header=False)


# aaa=aa[['PMBPOL', 'PMBFRACT','POLSIT','PMBMOD','PMBTXINT']]

# AExmTEST = pol.AExn(pol.age(), GKM95)

# pol.p.to_excel(path+'/zJO/check portefeuille.xlsx', header = True )
# aa.to_excel("check portefeuille.xlsx", header = True )


#Visualiser une dimension d'un numpy qui n'apparait pas
#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])
# AExn = pol.AExn()





# interp = pol.interp()