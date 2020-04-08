from Portefeuille import Portfolio
from Parametres import allRuns
import numpy as np
import pandas as pd
from varname import varname
import time
import os, os.path
#from MyPyliferisk import mortalitytables
from MyPyliferisk import Actuarial
from MyPyliferisk.mortalitytables import *
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

# =============================================================================
#   Création de la classe Sérénité
# =============================================================================
# tableFemmes = 'EKF05i'
# tableHommes = 'EKM05i'
    
class VE(Portfolio):
    mods=[1,11]

    # LapseTimine à 0.5 pour les VE
    lapseTiming = 0.5
            
    # tableFemmes = EKF95
    # tableHommes = EKM95
    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopVE()
        self.lapse()
        self.reserveForExp()
    
    # Fonction pour savoir si une police lapse, voir pourquoi elle est là
    def isLapse(self):
        lapse = self.zero()
        check1 = (self.frac() * (self.durationIf()+12)/12)
        check2 = np.floor((self.frac()*(self.durationIf()+12)/12))
        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        # choicelist = [lapse[:,:,:]==0, lapse[:,:,:] ==1 ]
        choicelist = [lapse[:,:,:]==0, lapse[:,:,:] ==0 ]
        myLapse=np.select(condlist, choicelist)
        # Le premier mois il n'y a pas de payement car la prime est payé en début de mois et les date de calcul sont en fin de mois
        myLapse[:,0,:] = 0
        
        return myLapse
    
    # Fonction des lapse, pareil qu'au dessus    
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
       
        # Dimensionner pour les runs et le portefeuille en appel    
        mylapse=mylapse[:,:,self.runs]
        
        # Prise en compte du taux fractionnel et de la mise en place avant un paiement
        frac=self.frac()
        
        # Fractionnement à 0 sont remplacer par 1
        frac[frac==0]=12
        # mylapse=1-(1-mylapse)**(1/frac)
        mylapse=1-(1-mylapse)**(1/12)
        
        mylapse= self.isLapse()*mylapse
        
        return mylapse
     
    # Loop qui calcule les maturités, inforce annuels et mensuels, nombre de morts, nombre de surrenders.    
    def loopVE(self):
        
        # Vecteur mise à zéro
        nbrPolIf=self.one()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrPolIfSM=self.zero()
        matRate=self.zero()
        
        # Déclaration de certains vecteurs
        polTermM=self.polTermM()
        matRate[polTermM + 1==self.durationIf()]=1
        qxy=self.qxyExpMens()
        lapse=self.lapse()
         
        # Début du loop
        for i in range(1,self.shape[1]):
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapse[:,i,:]*(1-self.lapseTiming)))
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxy[:,i,:]*self.lapseTiming))
            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]

        #Nombre de polices actives                                 
        self.nbrPolIf=nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM=nbrPolIfSM
        #Nombre d'échéances de contrat
        self.nbrMaturities=nbrMaturities
        #Nombre de décès
        self.nbrDeath=nbrDeath
        #Nombre d'annulation de contrat
        self.nbrSurrender=nbrSurrender
    
# =============================================================================
    ### FONCTIONS ACTUARIELLES
# =============================================================================       
    

    def ageInit(self):
        age = (self.p['Age1AtEntry'].to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age
    
    def ageFinal(self):
        age = ((self.p['Age1AtEntry'] + (self.p['residualTermM'] + self.p['DurationIfInitial'])/12).to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age

    # Fonction de calcul des Dx
    def Dx(self, x, table, tablestring):
        
         if x == 'x':
             myAge = self.ageInit().astype(int)
         elif x == 't':
             myAge = self.age().astype(int)
         elif x == 'n':
             myAge = self.ageFinal().astype(int)

         txTech = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis]/100
         # testech = self.p['PMBTXINT'].to_numpy()
         txTechLoop = np.unique(self.p['PMBTXINT'].to_numpy())
         
         tableMort = self.p['POLTBMORT'].to_numpy()[:,np.newaxis,np.newaxis]
         mask_tableMort = ((tableMort == tablestring)*self.one()).astype(bool)

         myDx = self.zero()
         for i in np.nditer(txTechLoop):
             txInt = i / 10000
             mask_txTech = ((txTech == txInt)*self.one()).astype(bool)
             mt = Actuarial(nt=table, i=txInt)
             aDx = pd.DataFrame(mt.Dx).to_numpy()
             myAge = np.where(myAge>=mt.w, mt.w-1, myAge)
             myDx[mask_txTech] = np.take(aDx, myAge[mask_txTech])
         return myDx


    # Fonction de calcul des Mx
    def Mx(self, myAge, table, tablestring):
         if x == 'x':
             myAge = self.ageInit().astype(int)
         elif x == 't':
             myAge = self.age().astype(int)
         elif x == 'n':
             myAge = myAge.astype(int)
         txTech = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis]/100
         myMx = self.zero()
         for i in range(0, 375, 25):
             txInt = i / 10000
             mask_txTech = ((txTech == txInt)*self.one()).astype(bool)
             mt = Actuarial(nt=table, i=txInt)
             aMx = pd.DataFrame(mt.Mx).to_numpy()
             myAge = np.where(myAge>=mt.w, mt.w-1, myAge)
             myMx[mask_txTech] = np.take(aMx, myAge[mask_txTech])
         return myMx
    
    # Fonction de calcul des Nx
    def Nx(self, myAge, table, tablestring):
         if x == 'x':
             myAge = self.ageInit().astype(int)
         elif x == 't':
             myAge = self.age().astype(int)
         elif x == 'n':
             myAge = myAge.astype(int)
         txTech = self.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis]/100
         myNx = self.zero()
         for i in range(0, 375, 25):
             txInt = i / 10000
             mask_txTech = ((txTech == txInt)*self.one()).astype(bool)
             mt = Actuarial(nt=table, i=txInt)
             aNx = pd.DataFrame(mt.Nx).to_numpy()
             myAge = np.where(myAge>=mt.w, mt.w-1, myAge)
             myNx[mask_txTech] = np.take(aNx, myAge[mask_txTech])
         return myNx

# =============================================================================
    ### CALCUL DES SURRENDER
# =============================================================================

    # VAL_SA_PP - capital de la police
    def insuredSum(self):
        sumAssdPp = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        return sumAssdPp
    
    # VAL_ACCRB_PP - valeur de la PB acquise en début de projection               
    def valAccrbPP(self):
        valAccrbPp = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        return valAccrbPp
    
    # ADUE_VAL - Annuité actuarielle
    def adueVal(self):
        polTerm = self.p['POLDURC'].to_numpy()[:,np.newaxis,np.newaxis]
        adueVal = polTerm - ((self.durationIf()+1)/12)
        adueVal = np.floor(adueVal)
        return adueVal

    # PMG_SA_PC - traitement des frais pour provGestPP
    def pmgSaPc(self):
        pmgSaPc = self.cgSaPriPc() * self.valNetpFac() + self.cgSaPolPc() * self.valPolFac()
        return pmgSaPc
       
    # PROV_GEST_PP - Provision de gestion par police, quelle logique?
    def provGestPP(self):
        provGestPp = self.pmgSaPc()/100 * (self.insuredSum() + self.valAccrbPP()) \
        - self.valNetpFac() * (self.prInventPP() - self.purePremium())
        return provGestPp
    
    # VAL_PREC_PP - risque en cours
    def valPrecPP(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        agelimite=(self.age()<=85)
        # Calcul du risque en cours
        riderIncPP=self.primeTotaleMensuelle()*self.isPremPay()*agelimite
        riderIncPP2=self.primeTotaleMensuelle()*agelimite
        precPPbis=self.zero()
        frek=self.frac()
        for i in range(1,self.shape[1]):
            precPPbis[:,i,:]=precPPbis[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result =[(precPPbis)]
        sinon = 0
        precPP = np.select(conditions,result,sinon)
        return precPP
    
    # PR_PURE_PP - Prime pure calcul éronné pour la mod11
    def purePremium(self):
        purePremium =  self.insuredSum() / 99
        return purePremium
   
    # Primes mensuelles (ne dépend pas de isprempay)
    def primeTotaleMensuelle(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotaleMensuelle = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] *self.one() / frac
        return primeTotaleMensuelle 

    # VAL_NETP_PP valeur des primes nettes
    def valNetpPP(self):
        ValNetpPp = self.purePremium() * self.valNetpFac()
        return ValNetpPp
    
    # PR_INVENT_PP
    def prInventPP(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        # result =[(self.purePremium() + (self.fraisGestion()/100 * self.insuredSum()))]
        result =[(self.purePremium() + ((self.cgSaPolPc()+self.cgSaPriPc())/100 * self.insuredSum()))]
        sinon = 0
        PrInventPp = np.select(conditions,result,sinon)
        return PrInventPp
      
    # VAL_NETP_FAC - durée restante mensuelle, à 0 si pas de paiement des primes
    def valNetpFac(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result = [(99 - (self.durationIf()/12))]
        sinon = 0
        valNetpFac = np.select(conditions,result,sinon)
        return valNetpFac
    
    # VAL_POL_FAC - durée restante mensuelle, ne dépend pas des primes
    def valPolFac(self):
        valPolFac = 99 - (self.durationIf()/12)
        return valPolFac
    
    # VAL_ZILL_PP - valeur de zillmérisation    
    def valZillPP(self):
        valZillPC = (5/100) * self.one()
        ValZillPP = np.minimum(valZillPC * self.prInventPP() * self.valNetpFac(), self.insuredSum() - self.valNetpPP() + self.provGestPP())
        return ValZillPP
    
    # MATH_RES_BA - provision mathématique - en cours
    def mathResBa(self):
        
        # pour la 11:
        # mathResBa = np.maximum(self.insuredSum() + self.valAccrbPP() + self.provGestPP() + self.valPrecPP() - self.valNetpPP() - self.valZillPP(), 0)
        
        # pour la 01:
        mathResBa = np.maximum(self.insuredSum()  + self.valPrecPP() - self.valNetpPP() - self.valZillPP(), 0)
        
        
        return mathResBa
    
# =============================================================================
    ### FRAIS -> INTEGRER PTF
# =============================================================================

    # Frais sur durée du contrat
    def cgSaPolPc(self):
        conditions = [(self.p['Age1AtEntry'] < 53), (self.p['Age1AtEntry'] < 70)]
        result =[(0.25), (0.45)]
        sinon = (0.9)
        cgSaPolPc = np.select(conditions,result,sinon)[:,np.newaxis,np.newaxis]
        return cgSaPolPc
    
    # Frais sur durée du paiement des primes
    def cgSaPriPc(self):
        conditions = [(self.p['Age1AtEntry'] < 53), (self.p['Age1AtEntry'] < 70)]
        result =[(0.35), (0.55)]
        sinon = (1.2)
        cgSaPriPc = np.select(conditions,result,sinon)[:,np.newaxis,np.newaxis]
        return cgSaPriPc
    
# =============================================================================
    ### FONCTIONS DOUBLONS
# =============================================================================

    # NO_SURRS - nombre de surrenders - a priori à effacer après vérification
    def numberSurrenders(self):
        noSurrs = self.nbrPolIfSM * self.lapse() * (1-self.lapseTiming*self.qxExpMens())
        return noSurrs
    
    # Prime totale, doublon à effecer après avoir corrigé les références
    def primeTotale(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotale = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] / frac * self.isPremPay()
        return primeTotale 

    # NO_DEATHS - nombre de morts
    def numberDeaths(self):
        noDeaths= self.qxExpMens() * self.nbrPolIfSM *(1 - self.lapse()*self.lapseTiming)
        return noDeaths
# =============================================================================
    ### CALCUL DE DEATHOUTGO
# =============================================================================    

    # DEATH_BEN_PP - calcul du death benefit
    def deathBenefit(self):
        capital = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]    
        frac = 12 / self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        pbAcq = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]
        durationif = self.durationIf()  
        isPremPay = self.isPremPay()
        conditions = [durationif[:,0,:] != 1, durationif[:,0,:] == 1]
        result =[np.ceil(durationif[:,0,:]/frac[:,0,:]), 1]
        isPremPay[:,0,:] = np.select(conditions,result)
        premiumsPaid = isPremPay * pol.p['POLPRTOT'][:,np.newaxis,np.newaxis]/pol.frac()           
        cumulatedPremiums = pol.zero()
        cumulatedPremiums = np.cumsum(premiumsPaid, axis=1)      
        conditions = [(durationif>12)]
        result =[(0)]
        sinon = 1
        deathBenPP1 = np.select(conditions,result,sinon) * cumulatedPremiums
        conditions = [(durationif>12)]
        result =[(1)]
        sinon = 0
        durationif12plus = np.select(conditions,result,sinon)
        deathBenPP2 = (capital + pbAcq) * durationif12plus  
        deathBenPP = deathBenPP1 + deathBenPP2
        return deathBenPP

# =============================================================================
    ### CALCUL DE TOTALEXPENSE
# =============================================================================
    # F_MATH_RES_IF - prov math actualisée avec les inforce
    def fMathResIf(self):
        fMathResIf = self.mathResBa() * self.nbrPolIf
        return fMathResIf    
   
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth ==1
        return mask*1
    
    def unitExpense(self):
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        coutParPolice=self.fraisGestion()
        cost=coutParPolice*inflation*self.nbrPolIfSM
        return cost

    #  Calcul des réserve mathématiques adjustées
    def reserveForExp(self):
        # déclaration des nouvelles variables
        totExp = self.zero()
        rfinAnn = self.zero()
        adjMathRes2 = self.zero()
        resFinMois = self.zero()
        provMathAj = self.zero()
        totCom = self.totalCommissions()

        # fonction existantes
        fMathResIf = self.fMathResIf()
        riderCoutgo = self.ridercOutgo()
        premInc = self.totalPremium()
        # mathResPP = self.mathResBa()
        # pupMathRes = self.pupMathRes()
        provMathIf = self.mathResBa() * self.nbrPolIf
        mUfii = self.rate()
        # durationIf = self.durationIf()
        monthPb = self.one() - self.allocMonths()
        # isActive = self.isActive()
        
        # PPURE_ENC
        premInvest = self.purePremium() * self.nbrPolIfSM / self.frac() * self.isPremPay()
        
        unitExp = self.unitExpense()
        # provTechAj = self.provTechAj()   
        txReserve = self.fraisGestionPlacement()
    
        # calcul des exceptions
        provMathAj[:,0,:] = premInc[:,0,:] - totExp[:,0,:] - riderCoutgo[:,0,:]

        for i in range(1,self.shape[1]):
            # Calcul adjMathRes2
            adjMathRes2[:,i,:] = np.maximum(0, fMathResIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:])
            
            # Calcul totExp
            totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
            
            # Calcul ProvMathAj
            provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - (totExp[:,i,:] + totCom[:,i,:])
            
            # Calcul resFinMois, en ordre
            resFinMois[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            
            # Calcul RFIN_ANN_NC, en ordre
            # if durationIf[:,i,:] % 12 != self.zero():
            #     rfinAnn[:,i,:] = rfinAnn[:,i-1,:] + resFinMois[:,i,:]
            # else:
            #     rfinAnn[:,i,:] = 0
            rfinAnn[:,i,:] = (rfinAnn[:,i-1,:] + resFinMois[:,i,:]) * monthPb[:,i,:] 

   #Définition des variables récursives
        # Résultat financier en fin de mois non constaté
        self.resFinMois = resFinMois
        # Résultat de l'année en cours non constaté
        self.rfinAnn = rfinAnn
        # Reserves mathématiques ajustées pour calculer les expenses
        self.adjMathRes2 = adjMathRes2
        # Provisions mathématiques ajustées
        self.provMathAj = provMathAj
        # Total des expenses
        self.totExp = totExp
        self.provMathIf = provMathIf

    
    # PPURE_ENC
    def ppureEnc(self):
        # Complètement faux, Prophet divise la prime pure mensuelle par le
        # fractionnemenet et multiplie le résultat par les inforce...
        # alors que la prime pure fractionnée est déjà calculée ailleurs
        ppureEnc = pol.nbrPolIfSM * pol.purePremium() / pol.frac() * pol.isPremPay()
        # Correct:
        # ppureEnc = pol.nbrPolIfSM * pol.purePremium() * (12/pol.frac()) * pol.isPremPay()
        return ppureEnc
        
# =============================================================================
    ### CALCUL DES CLAIMS   
# =============================================================================
    def surrOutgo(self):
        conditions = [(self.durationIf()>36)]
        result =[(self.mathResBa() * self.numberSurrenders())]
        sinon = 0
        surrOutgo = np.select(conditions,result,sinon)
        
        # surrOutgo = self.mathResBa() * self.numberSurrenders()
        return surrOutgo
    
    def deathOutgo(self):
        deathOutgo = self.deathBenefit() * self.numberDeaths()
        return deathOutgo
    
    def ridercOutgo(self):
        
        # old code 
        # situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        # conditions = [(self.age() <= 85) & (situation != 4) & (situation != 8) & (situation != 9)]
        # # Attention:
        # result =[(self.totalPremium() * self.dcAccident())]
        # # Faux, il ne faut pas prendre la prime totale mais la prime accident
        # sinon = 0
        # ridercOutgo = np.select(conditions,result,sinon)
        
        totalPremium = self.totalPremium()
        cpl3 = (self.p['POLPRCPL3'])[:,np.newaxis,np.newaxis]/self.frac()
        dcAccident = self.dcAccident()    
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        ridercOutgo = self.zero()
        zero = self.zero()
        isPremPay = self.isPremPay()
        nbrPolIfSM = self.nbrPolIfSM
        
        mask_infeqf85 = (self.age() <= 85) & (situation != 4) & (situation != 8) & (situation != 9)
        mask_sup85 = (self.age() > 85) & (situation != 4) & (situation != 8) & (situation != 9)  
        
        ridercOutgo[(self.mask([11])) & mask_infeqf85] = totalPremium[(self.mask([11])) & mask_infeqf85] * dcAccident[(self.mask([11])) & mask_infeqf85]
        ridercOutgo[(self.mask([11])) & mask_sup85] = zero[(self.mask([11])) & mask_sup85] 
        
        ridercOutgo[(self.mask([1])) & mask_infeqf85] = cpl3[(self.mask([1])) & mask_infeqf85] * dcAccident[(self.mask([1])) & mask_infeqf85] * isPremPay[(self.mask([1])) & mask_infeqf85] * nbrPolIfSM[(self.mask([1])) & mask_infeqf85]
        ridercOutgo[(self.mask([1])) & mask_sup85] = zero[(self.mask([1])) & mask_sup85] 
    
        return ridercOutgo

# =============================================================================
    ### CALCUL DU BEL
# =============================================================================
# Retourne les primes totales perçues
    def totalPremium(self):
        
        primetot = (self.p['POLPRTOT'])[:,np.newaxis,np.newaxis]/self.frac()
        primecompl = (self.p['POLPRCPL3'])[:,np.newaxis,np.newaxis]/self.frac() 
        modalite = (self.p['PMBMOD'])[:,np.newaxis,np.newaxis]
        
        conditions = [(self.age() <= 85) | (modalite == 11), (self.age() > 85) & (modalite == 1)]
        result =[(primetot), (primetot - primecompl)]
        premInc = np.select(conditions,result) 
        
        prem=premInc*self.nbrPolIfSM*self.isPremPay()*self.indexation()
        
        return prem


#Retourne le total des prestations payés 
    def totalClaim(self):
        return self.deathOutgo() + self.ridercOutgo() + self.surrOutgo()

#Retourne le total des commissions payées
    # def totalCommissions(self):
    #     return self.totalPremium() * self.commissions()

#Retourne les dépense totales 
    def totalExpense(self):
        # return self.initialExpenses() + self.renewableExpenses()
        totalExpense = self.totExp
        return totalExpense

# =============================================================================
    # --- Calcul du BEL   
# =============================================================================
    # def BEL(self):
        
    #     interestRates=1+self.rate()       
    #     premium=self.totalPremium()
    #     claim=self.totalClaim()
    #     expense=self.totalExpense()
    #     commission=self.totalCommissions()
        
    #     bel=self.zero()
              
    #     for t in range(1,self.shape[1]+1):
    #         bel[:,-t,:]=(bel[:,-t+1,:]+claim[:,-t+1,:]+expense[:,-t+1,:]+commission[:,-t+1,:]-premium[:,-t+1,:])/interestRates[:,-t+1,:]
    
    
    #     return bel

    
pol = VE()




# dx = pol.Dx('t', EKF05I1, 'EKF05I1')





x = 't' 
table = EKF05I1 
tablestring = 'EKF05I1'
pol.p['POLTBMORT'] = pol.p['POLTBMORT'].str.strip()
        
if x == 'x':
    myAge = pol.ageInit().astype(int)
elif x == 't':
    myAge = pol.age().astype(int)
elif x == 'n':
    myAge = pol.ageFinal().astype(int)

txTech = pol.p['PMBTXINT'].to_numpy()[:,np.newaxis,np.newaxis]/100
# testech = pol.p['PMBTXINT'].to_numpy()
txTechLoop = np.unique(pol.p['PMBTXINT'].to_numpy())

tableMort = pol.p['POLTBMORT'].to_numpy()[:,np.newaxis,np.newaxis]
mask_tableMort = ((tableMort == tablestring)*pol.one()).astype(bool)

myDx = pol.zero()
for i in np.nditer(txTechLoop):
    txInt = i / 10000
    mask_txTech = ((txTech == txInt)*pol.one()).astype(bool)
    mt = Actuarial(nt=table, i=txInt)
    aDx = pd.DataFrame(mt.Dx).to_numpy()
    myAge = np.where(myAge>=mt.w, mt.w-1, myAge)
    myDx[mask_txTech & mask_tableMort] = np.take(aDx, myAge[mask_txTech & mask_tableMort])














 
x = pol.p

x.to_excel(path+'/zFT/ptf.xlsx')

monCas = pol.qx()
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zFT/check.csv',header=False)
