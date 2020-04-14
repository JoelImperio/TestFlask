from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
from MyPyliferisk import Actuarial, AExn
from MyPyliferisk.mortalitytables import *
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()


##############################################################################################################################
#Création de la class Epargne
############################################################################################################################

class MI(Portfolio):
    mods=[2,10,6,7]

#Products: F1XT_1,F2XT_1,F1XT14,F1XT11
    
    # age limite pour la garantie complémentaire CPL1
    ageLimiteCPL1 = 60
    ageLimiteCPL2 = 65
    tableHommes = EKM1995
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        
        
        # self.Nx = self.actu('Nx', 'x')
        # self.Nxn = self.actu('Nx', 'n')
        # self.Nxt = self.actu('Nx', 't')
        # # Nxp = self.actu('Nx', 'p')
        # self.NxDec = self.actu('Nx', 't+1')
        
        # self.Dx = self.actu('Dx', 'x')
        # self.Dxn = self.actu('Dx', 'n')
        # self.Dxt = self.actu('Dx', 't')
        # # Dxp = self.actu('Dx', 'p')
        # self.DxDec = self.actu('Dx', 't+1')
        
        # self.Mx = self.actu('Mx', 'x')
        # self.Mxn = self.actu('Mx', 'n')
        # self.Mxt = self.actu('Mx', 't')
        # # Mxp = self.actu('Mx', 'p')
        # self.MxDec = self.actu('Mx', 't+1')




#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        # self.commutations()
        self.loopSaving()
        self.reserve()
        
  
        
  
  
# # Fonction présent dans l'update permettant de chargé une fois tous les symboles de commutation
    # def commutations(self):
        

        
    #     self.Nx = self.actu('Nx', 'x')
    #     self.Nxn = self.actu('Nx', 'n')
    #     self.Nxt = self.actu('Nx', 't')
    #     # Nxp = self.actu('Nx', 'p')
    #     self.NxDec = self.actu('Nx', 't+1')
        
    #     self.Dx = self.actu('Dx', 'x')
    #     self.Dxn = self.actu('Dx', 'n')
    #     self.Dxt = self.actu('Dx', 't')
    #     # Dxp = self.actu('Dx', 'p')
    #     self.DxDec = self.actu('Dx', 't+1')
        
    #     self.Mx = self.actu('Mx', 'x')
    #     self.Mxn = self.actu('Mx', 'n')
    #     self.Mxt = self.actu('Mx', 't')
    #     # Mxp = self.actu('Mx', 'p')
    #     self.MxDec = self.actu('Mx', 't+1')
  
    
  


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
        
        # nbrPolIf = self.one()
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
        
    # Modification les mixtes 2 tetes sont en fait calculée en fonction de l'assuré 1 (Ce qui est faux)
        mask = (((self.p['PMBMOD']==2) & (self.p['POLNBTETE']==2))).astype(bool)
   

        qxy[mask] = qx[mask] + qx[mask] - qx[mask]*qx[mask]
        qxy[mask] = 1-(1-qxy[mask])**(1/12)
        
        
        
        qxyD = lapseTiming * qxy
        txInteret = self.txInt()
        # prEncInv = self.premiumInvested()

        
        # Variable actuarielle
        AExn = self.AExn()




        #Définition du vecteur des maturités (bool)        
        matRate[polTermM+1 ==self.durationIf()]=1 
            
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


        return


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
    
    




# Arrondi des tables afin d'obtenir taux pb (table rdt est)
    def txPartPB(self):
        
        rate = (1+self.pbRate())**12 - 1
        rate = (1+rate)**(1/12) - 1
        rate = np.round(rate, decimals = 6)
        return rate
    



# =============================================================================
    ### FONCTIONS ACTUARIELLES
# =============================================================================       
    

    def ageInit(self):
        age = (self.p['Age1AtEntry'].to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age
    
    def ageFinal(self):
        age = ((self.p['Age1AtEntry'] + (self.p['residualTermM'] + self.p['DurationIfInitial'])/12).to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age
        
    
    
 # Fonction générique actuarielle
    def actu(self, var, x):
        
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
            
        txTech = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis]/100
        txTechLoop = np.unique(self.p['PMBTXINT'].to_numpy())
        tbMort = tbMort[:,np.newaxis,np.newaxis]
        myVarx = self.zero()
        
        for tb in table:
             
            mask_tableMort = ((tbMort == tb)*self.one()).astype(bool)
        
            for i in np.nditer(txTechLoop):
                
                txInt = i / 100
                mask_txTech = ((txTech == txInt)*self.one()).astype(bool)
                mt = Actuarial(nt=eval(tb), i=txInt)
                
                aVARx = pd.DataFrame(getattr(mt, var)).to_numpy()
                    
                myAge = np.where(myAge>=mt.w, mt.w-1, myAge)
                myVarx[mask_txTech & mask_tableMort] = np.take(aVARx, myAge[mask_txTech & mask_tableMort])
          
        
            
        return myVarx 






   
# AExn Endowment insurance
    def AExn(self):
        

        Mx = self.actu('Mx','t')
        Mxn = self.actu('Mx','n')
        Dx = self.actu('Dx','t')
        Dxn = self.actu('Dx','n')
        
        AExn = (Mx - Mxn + Dxn) / Dx
        AExn = np.roll(AExn, -1, axis = 1)

        
        MxDec = self.actu('Mx','t+1')
        MxnDec = Mxn
        DxDec = self.actu('Dx','t+1')
        DxnDec = Dxn
        
        AExnDec = (MxDec - MxnDec + DxnDec) / DxDec
        AExnDec = np.roll(AExnDec, -1, axis = 1)
        
        resultat = self.interp(AExn, AExnDec)
        
        return resultat
    
    
    
# äxn annuity endowment insurance
    def axn(self):
        
        Nxn = self.actu('Nx','n')
        Nx = self.actu('Nx','t')
        Dx = self.actu('Dx','t')
        
        axn = (Nx - Nxn) / Dx
        axn = np.roll(axn, -1, axis = 1)
        
        NxDec = self.actu('Nx','t+1')
        DxDec = self.actu('Dx','t+1')
        
        axnDec = (NxDec - Nxn) / DxDec
        axnDec = np.roll(axnDec, -1, axis = 1)
        
        resultat = self.interp(axn, axnDec)
        
        return resultat
    
    
# AExn initial = Net Single Premium
    def AExnInit(self):

        Mx = self.actu('Mx','x')
        Mxn =  self.actu('Mx','n')
        Dx = self.actu('Dx','x')
        Dxn =  self.actu('Dx','n')
        
        AExn = (Mx - Mxn + Dxn) / Dx

        return AExn
    

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
# Calcul des Claims
# =============================================================================

# retourne la somme assurée avec le bon format
    def sumAss(self):
        
        sumAss = self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one()   
        return sumAss








# Provision zillmérisée cumulée entre 2 calcul de PB (PMZ_ZILL_CUM)
    def pmZillCum(self):
        
        pass
    

# Provision technique zillmérisée (PMT_ZILL_PP)
    def pmZill(self):
        
        pm = self.pmTech() - valZill(self)
        return pm



# Calcul des primes d'inventaire annuelle (PA'')
    def prInventaire(self):
        
        loading = self.p['aquisitionLoading'][:,np.newaxis, np.newaxis]*self.one()   
        fraisFract = self.p['fraisFract'][:,np.newaxis, np.newaxis]*self.one()   
        premInc=((self.p['POLPRVIEHT'] - self.p['POLPRCPLA'])[:,np.newaxis,np.newaxis])
        premInc = premInc * self.indexation()
        prInventaire = premInc * (1-loading) / fraisFract
        return prInventaire
        
  
    
# Calcul des primes pures PR PURE PP
    def prPure(self):
        
        gestLoading = self.p['gestionLoadingSA'][:,np.newaxis, np.newaxis]*self.one() 
        capital = self.p['PMBCAPIT'][:,np.newaxis, np.newaxis]*self.one()  
        prInvent = self.prInventaire()
        ppure = prInvent - gestLoading * capital
        return ppure
        

# Valeur actualisée des primes nettes
    def valNetPrem(self):
        
        premNet = self.prPure()
        axn = self.axn()
        valNetPrem = premNet * axn
        return valNetPrem

# Valeur actualisé SA (Net single premium value) AExn * capital
    def valSaPP(self):
        
        # mask ici car au moment de l'échéance de la police, le net Single premium = 0 et non Capital
        mask = self.polTermM() > self.durationIf() 
        valSaPP = self.zero()
        valSaPP[mask] = self.AExn()[mask] * self.sumAss()[mask]
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




# Retourne la zillmérisation VAL_ZILLMER
    def zillmer(self):
        
        PA = self.prInventaire()
        
        # taux de zillmérisation
        alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
        axn = self.axn()
        zill = alpha * PA * axn
        
        


        return zill





# loop pour calculer les reserves
    def reserve(self):
        
        
        # Variable existante
        zill = self.zero()
        precPP = self.precPP()
        valSaPP = self.valSaPP()
        valNetPP = self.valNetPrem()
        AExn = self.AExn()
        prInventPP = self.prInventaire()
        alpha = self.p['tauxZill'][:,np.newaxis, np.newaxis]*self.one()  
        axn = self.axn()
        valSumAss = self.sumAss() * self.AExn()
        
        
        # Nouvelles variables
        valAccrbPP = self.zero()
        pbIncorPP = self.zero()
        pbAcquPP = self.zero()
        pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pbCalcPP = self.zero()
        isActive = self.isActive()
        mathResPP = self.zero()
        provGestPP = self.zero()
        provTechPP = self.zero()
        pmZillCum = self.zero()
        pmZillPP = self.zero()
        pmPourPB = self.zero()
        tierPM = self.zero()
        zillTot = self.zero()
        
        
        #Variables de l'épargne actifs et réduits
        epargnAcquPP = self.zero()        
        eppAcquAPPUP = self.zero()
        epAcquAVPUP = self.zero()

        epargnAcquPP[:,0,:] = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]        

#Variables de PB actifs et réduites

        pbAcquAVPUP = self.zero()
        pbAcquAPPUP = self.zero()
        pbIncorPUP = self.zero()      
        epgTxPbPUP = self.zero()
        pbCalcPUP = self.zero()
        pbPupDTHS = self.zero()
        pbSortDTHS = self.zero()
        
        epgTxPbPUP[:,0,:] = 0
        
        pbSortMatsPP= self.zero()
        pbSortMatsPUP = self.zero()
        allocMonths = self.allocMonths()
        
        # Variable existante
        pmFirstYear = self.pmFirstYear()
    
   
        # Taux annualisé
        txIntPC = self.txInt()**(12) - 1
        # txPbPC = self.txPbPC()/100
        
        # taux annualisé
        txIntPC = self.txInt()**(12) - 1
        txPartPB = self.txPartPB()
        
        # txTot = 1 + (txPbPC + txIntPC)
        

        
        
        pbCalcPPdths = self.zero()
        pbCalcPUPdths = self.zero()
        
     
        # nouvelles variables
        pmPourPB = self.zero()
        
        
        
        
        for i in range(1,self.shape[1]):
        
        
        
        # #Définition des variables d'épargne pour actives et réduites
#             epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]

#             epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
#             epTemp = epAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + epargnAcquPP[:,i,:] * nbrNewRed[:,i,:]
            
#             eppAcquAPPUP[:,i,:] = np.divide(epTemp,nbrPupsIf[:,i,:],out=np.zeros_like(epTemp), where=nbrPupsIf[:,i,:]!=0)

            
# # #Définition des variables de PB pour actives et réduites  
    

            
#             pbIncorPUP[:,i,:] = np.nan_to_num(pbCalcPUP[:,i-1,:]  * isActive[:,i-1,:]) 
            
#             pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:]) * txInteret[:,i,:] * isActive[:,i,:] 


            pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
            pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:])  * isActive[:,i,:]             

            valAccrbPP[:,i,:] = pbAcquPP[:,i,:] * AExn[:,i,:] 
            
            tierPM[:,i,:] = (1/3) * np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] + precPP[:,i,:] - valNetPP[:,i,:], 0)
            
            zillTot[:,i,:] = np.minimum(alpha[:,i,:] * prInventPP[:,i,:] * axn[:,i,:], np.maximum(valSumAss[:,i,:] - valNetPP[:,i,:], 0))
            
            
            zill[:,i,:] = np.where(tierPM[:,i,:] < zillTot[:,i,:], tierPM[:,i,:], zillTot[:,i,:])
            
         
                
                
            
            mathResPP[:,i,:] = np.maximum(valSaPP[:,i,:] + valAccrbPP[:,i,:] - valNetPP[:,i,:] + precPP[:,i,:] - zill[:,i,:], 0 )

            provTechPP[:,i,:] = mathResPP[:,i,:] - provGestPP[:,i,:] - precPP[:,i,:] + zill[:,i,:]
            
            pmZillPP[:,i,:] = provTechPP[:,i,:] - zill[:,i,:]
            
            pmZillCum[:,i,:] = pmZillPP[:,i,:] + (1-allocMonths[:,i-1,:]) * pmZillCum[:,i-1,:]
            
            
            pmPourPB[:,i,:] = (pmZillCum[:,i,:] * pmFirstYear[:,i,:]/12) * allocMonths[:,i,:]
            
            
            pbCalpTEMP = pmPourPB[:,i,:] * txPartPB[:,i,:] * (pmFirstYear[:,i,:] / 12)
            
            pbCalcPP[:,i,:] = np.divide( pbCalpTEMP, AExn[:,i,:], out=np.zeros_like(pbCalpTEMP), where=AExn[:,i,:]!=0 ) * allocMonths[:,i,:]
            
            
            
            
            
            

#             pbSortDTHS[:,i,:] = np.nan_to_num(pbCalcPPdths[:,i,:] * isActive[:,i,:]) 
            
#             pbPupDTHS[:,i,:] = np.nan_to_num(pbCalcPUPdths[:,i,:] * isActive[:,i,:]) 
         
#             pbAcquAVPUP[:,i,:] = (pbAcquAPPUP[:,i-1,:] + pbIncorPUP[:,i,:]) * txInteret[:,i,:]

     

#             pbTemp=pbAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + pbAcquPP[:,i,:] * nbrNewRed[:,i,:]            
            
#             pbAcquAPPUP[:,i,:] = np.divide(pbTemp,nbrPupsIf[:,i,:],out=np.zeros_like(pbTemp), where=nbrPupsIf[:,i,:]!=0)       
  
#             epgTxTEMP = epgTxPbPUP[:,i-1,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) * (txTot[:,i,:]**(1/12)) + (epgTxPB_PP[:,i,:] *  nbrNewRed[:,i,:])
            
#             epgTxPbPUP[:,i,:] =  np.divide(epgTxTEMP, nbrPupsIf[:,i,:], out=np.zeros_like(epgTxTEMP), where=nbrPupsIf[:,i,:]!=0)
            
            
            
               

            
            
            
#             pbCalcPUP[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * allocMonths[:,i,:]
            
#             pbCalcPPdths[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
#             pbCalcPUPdths[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
#             pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
#             pbSortMatsPUP[:,i,:] = pbCalcPUP[:,i,:] * isActive[:,i,:]





# #Sauvegarde des variables d'éparnge actifs et réduites
        
#         #Epargne acquise par police AVANT nouvelle réduction                                 
#         self.epAcquAVPUP=epAcquAVPUP
#         #Epargne acquise par police APRES nouvelle réduction 
#         self.eppAcquAPPUP=eppAcquAPPUP
#         #Epargne aquise des polices actives
#         self.epargnAcquPP = epargnAcquPP



# #Sauvgarde des variables de  PB pour actives et réduites
        
#         # PB acquise par police AVANT nouvelle réduction                                 
#         self.pbAcquAVPUP=np.nan_to_num(pbAcquAVPUP)
#         # PB acquise par police APRES nouvelle réduction 
#         self.pbAcquAPPUP=np.nan_to_num(pbAcquAPPUP)
#         #  PB à affecter par police réduite
#         self.pbCalcPUP = pbCalcPUP
#         # epargne et PB des polices réduites calculé au taux PB
#         self.epgTxPbPUP = epgTxPbPUP
#         # PB incorporée par contrat réduit
#         self.pbIncorPUP = pbIncorPUP
#         # Montant de PB à affecter par police
        self.pbCalcPP = pbCalcPP
#         # PB acquise des polices actives
        self.pbAcquPP = pbAcquPP
#         # PB incorporée par police
#         self.pbIncorPP = pbIncorPP
#         # PB incorporée par police réduite
#         self.pbIncorPUP = pbIncorPUP
#         # PB non incorporée des polices réduites
#         self.pbPupDTHS=pbPupDTHS
#         # PB non incorporée des polices actives
#         self.pbSortDTHS=pbSortDTHS
#         # Pb donnée par police en cas de maturité
#         self.pbSortMatsPP = pbSortMatsPP
#         # pb donnée par police en cas de maturité d'une police réduite
#         self.pbSortMatsPUP = pbSortMatsPUP     
#         # pb donnée par police en cas de décès
#         self.pbCalcPPdths = pbCalcPPdths
#         # pb donné par police en cas de décès d'une police réduite
#         self.pbCalcPUPdths = pbCalcPUPdths
        






        self.pmPourPB = pmPourPB
        self.pmZillCum = pmZillCum
        self.provTechPP = provTechPP
        self.mathResPP = mathResPP
        self.valAccrbPP = valAccrbPP
        self.pbIncorPP = pbIncorPP
        self.pmZillPP = pmZillPP
        self.valAccrbPP = valAccrbPP
        self.zill = zill

# PB acquise depuis le début du contrat (SUREMENT A MODIFIER)
    def pbAcquPP(self):
        
        pb = self.p['PMBPBEN'][:,np.newaxis,np.newaxis] * self.one()

        return pb
    
    
    
    

# retourne un vecteur de 1 à 12 selon la duration de la police, si + élevé de 12 mois alors 12
    def firstYear(self):
        dur = self.durationIf()
        dur[dur>12] = 12 
        return dur




#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        
        deathBenPP = self.sumAss() + self.pbAcquPP()
        deathOutgo = deathBenPP * self.nbrDeath
        
        
        return deathOutgo

#Retourne les claims des garanties complémentaires (RIDERC_OUTGO)
    def claimCompl(self):
        return self.zero()

#Retourne les rachats totaux (SURR_OUTGO)
    def surrender(self):
        return self.zero()

#Retourne les rachats partiels (PARTSV_OUTGO)
    def partialSurrender(self):
        return self.zero()

#Retourne les échéances (MAT_OUTGO)
    def maturity(self):
        return self.zero()


##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################


def tester(self):
    return self

pol = MI()
#pol=MI(run=[4,5])

    ###  Mod 2_1 produit F1XT1
# pol.ids([106907])

pol.ids([106907])
# pol.ids([301])
# pol.modHead([2],1)

    ### Mod 2_2 F2XT_1
# pol.ids([2135101])
# pol.modHead([2],2)

    ### Mod 10 F1XT14
# pol.ids([1602604])
# pol.mod([10])

    ### Mod 6 F1XT11
# pol.ids([799003])
# pol.mod([6,7])
# age = pol.age()


check = pol.valAccrbPP
# pureprem = pol.purePremium()

# a = pol.p
b=pol.nbrPolIf
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