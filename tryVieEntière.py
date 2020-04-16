from Portefeuille import Portfolio
from Parametres import allRuns
import numpy as np
import pandas as pd
from varname import varname
import time
import os, os.path
import datetime
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
    mods=[1, 11]

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
        # self.lapse()
        # self.isActive()
        self.commutations()
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
        self.nbrPolIf = nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM=nbrPolIfSM
        #Nombre d'échéances de contrat
        self.nbrMaturities=nbrMaturities
        #Nombre de décès
        self.nbrDeath=nbrDeath
        #Nombre d'annulation de contrat
        self.nbrSurrender=nbrSurrender
        
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask
    
    def policeActive(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis] * self.one()
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result =[(1)]
        sinon = 0
        policeActive = np.select(conditions,result,sinon)
        return policeActive
    
    def payPrimes(self):
        durationIf = self.durationIf()
        payPrimes = self.one()
        moisPaiement = (self.p['POLDURP'].to_numpy() * 12 )[:,np.newaxis,np.newaxis] * self.one()
        conditions = [(durationIf <= moisPaiement)]
        result =[(1)]
        sinon = 0
        payPrimes = np.select(conditions,result,sinon)
        return payPrimes
        
  
# =============================================================================
    ### FONCTIONS ACTUARIELLES
# =============================================================================       
    
    def ageInit(self):
        age = (self.p['Age1AtEntry'].to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age
    
    def ageFinal(self):
        age = ((self.p['Age1AtEntry'] + (self.p['residualTermM'] + self.p['DurationIfInitial'])/12).to_numpy()[:,np.newaxis,np.newaxis]*self.one())
        return age
    
    def agePrimes(self):
        age = ((self.p['Age1AtEntry'].to_numpy() + self.p['POLDURP'].to_numpy())[:,np.newaxis,np.newaxis]*self.one())
        return age
        
    # Fonction qui sert à retourner les valeurs actuarielles, Ax, ax, etc.
    def commutations(self):
        
        # Création des variables actuarielles utilisées
        Nx = self.actu('Nx', 'x')
        Nxt = self.actu('Nx', 't')
        Nxp = self.actu('Nx', 'p')
        NxtDec = self.actu('Nx', 't+1')
        Dxt = self.actu('Dx', 't')
        DxtDec = self.actu('Dx', 't+1')
        Mx = self.actu('Mx', 'x')
        Mxt = self.actu('Mx', 't')
        MxtDec = self.actu('Mx', 't+1')

        # Calcul de ax
        ax = self.zero()
        ax[Dxt>0] = Nxt[Dxt>0] / Dxt[Dxt>0]
        ax = np.roll(ax, -1, axis = 1)
        axDec = self.zero()
        axDec[DxtDec>0] = NxtDec[DxtDec>0] / DxtDec[DxtDec>0]
        axDec = np.roll(axDec, -1, axis = 1)
        ax = self.interp(ax, axDec)
        
        # Calcul de axp
        axp = self.zero()
        axp[Dxt>0] = (Nxt[Dxt>0] - Nxp[Dxt>0]) / Dxt[Dxt>0]
        axp = np.roll(axp, -1, axis = 1)
        axpDec = self.zero()
        axpDec[DxtDec>0] = (NxtDec[DxtDec>0] - Nxp[DxtDec>0]) / DxtDec[DxtDec>0]
        axpDec = np.roll(axpDec, -1, axis = 1)
        axp = self.interp(axp, axpDec)
        
        # Calcul de Ax
        Ax = self.zero()
        Ax[Dxt>0] = Mxt[Dxt>0] / Dxt[Dxt>0]
        Ax = np.roll(Ax, -1, axis = 1)
        AxDec = self.zero()
        AxDec[DxtDec>0] = MxtDec[DxtDec>0] / DxtDec[DxtDec>0]
        AxDec = np.roll(AxDec, -1, axis = 1)
        Ax = self.interp(Ax, AxDec)
        
        # Calcul de aduePolVal
        aduePolVal = Nx / (Nx - Nxp)
        
        # Calcul de axInitPrimes
        axInitPrimes = (Nx - Nxp) / Mx
        
        # Retour des variables voulues
        self.ax = ax
        self.axp = axp
        self.Ax = Ax
        self.aduePolVal = aduePolVal
        self.axInitPrimes = axInitPrimes
      
         
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
                mt = Actuarial(nt=eval(tb), i=txInt)
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
        # return resultat 
        

# =============================================================================
    ### CALCUL DES SURRENDER
# =============================================================================

    # SUM_ASSD_PP - capital de la police
    def insuredSum(self):
        sumAssdPp = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        return sumAssdPp
    
    # VAL_SUM_ASSD
    def valSumAssd(self):
        # valSaPP = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one() * self.Ax()
        valSaPP = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one() * self.Ax
        return valSaPP
    
    # VAL_ACCRB_PP - valeur de la PB acquise en début de projection               
    def valAccrbPP(self):
        valAccrbPp = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        return valAccrbPp
    
    # # ADUE_VAL - Annuité actuarielle
    # def adueVal(self):
    #     polTerm = self.p['POLDURC'].to_numpy()[:,np.newaxis,np.newaxis]
    #     adueVal = polTerm - ((self.durationIf()+1)/12)
    #     adueVal = np.floor(adueVal)
    #     return adueVal

    # PMG_SA_PC - traitement des frais pour provGestPP
    def pmgSaPc(self):
        pmgSaPc = self.cgSaPriPc() * self.valNetpFac() + self.cgSaPolPc() * self.valPolFac()
        return pmgSaPc
       
    # PROV_GEST_PP - Provision de gestion par police, quelle logique?
    def provGestPP(self):
        provGestPp = self.pmgSaPc() * (self.insuredSum() + self.valAccrbPP()) \
        - self.valNetpFac() * (self.prInventPP() - self.purePremium())
        return provGestPp
    
    # VAL_PREC_PP - risque en cours
    def valPrecPP(self):
        agelimite=(self.age()<=85)
        primecompl = (self.p['POLPRCPL3'])[:,np.newaxis,np.newaxis] / self.frac()
        riderIncPP = self.zero()
        riderIncPP2 = self.zero()
        primeTotaleMensuelle = self.primeTotaleMensuelle()
        isPremPay = self.isPremPay()
        payPrimes = self.payPrimes()
        
        # Calcul du risque en cours
        riderIncPP = primecompl * self.isPremPay() * agelimite * payPrimes
        riderIncPP2 = primecompl * agelimite * payPrimes
        
        
        riderIncPP[(self.mask([11]))] = primeTotaleMensuelle[(self.mask([11]))] * isPremPay[(self.mask([11]))] * agelimite[(self.mask([11]))] 
        riderIncPP2[(self.mask([11]))] = primeTotaleMensuelle[(self.mask([11]))] * agelimite[(self.mask([11]))] 
        
        
        precPPbis=self.zero()
        frek=self.frac()
        for i in range(1,self.shape[1]):
            precPPbis[:,i,:] = precPPbis[:,i-1,:] + riderIncPP[:,i,:] - ((frek[:,i,:] / 12) * riderIncPP2[:,i,:])
        
        precPP = precPPbis * self.isActive()
        return precPP
    
    # def valSaFac(self):
    #     valSaFac = self.abar()
    #     return valSaFac
        
        
    # PR_PURE_PP - Prime pure calcul éronné pour la mod11
    def purePremium(self):
        # purePremium = self.insuredSum() / self.axInit() * self.policeActive()
        # purePremium = self.insuredSum() / self.axInitPrimes() * self.policeActive() * self.payPrimes()
        purePremium = self.insuredSum() / self.axInitPrimes * self.policeActive() * self.payPrimes()
        
        # calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        insuredSum = self.insuredSum()
        purePremium[(self.mask([11]))] =  insuredSum[(self.mask([11]))] / 99
        return purePremium
   
    # Primes mensuelles (ne dépend pas de isprempay)
    def primeTotaleMensuelle(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotaleMensuelle = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one() / frac
        return primeTotaleMensuelle 

    # VAL_NETP_PP valeur des primes nettes
    def valNetpPP(self):
        
        ValNetpPp = self.purePremium() * self.valNetpFac()
        return ValNetpPp
    
    # PR_INVENT_PP
    def prInventPP(self):
        purePremium = self.purePremium()
        cgSaPolPc = self.cgSaPolPc()
        cgSaPriPc = self.cgSaPriPc()
        insuredSum = self.insuredSum()
        policeActive = self.policeActive()
        aduePolVal = self.aduePolVal
        
        prInventPp = self.zero()
        
        prInventPp[(self.mask([11]))] = purePremium[(self.mask([11]))] + (cgSaPolPc[(self.mask([11]))]+cgSaPriPc[(self.mask([11]))] * insuredSum[(self.mask([11]))]) * policeActive[(self.mask([11]))]
        prInventPp[(self.mask([1]))] = purePremium[(self.mask([1]))] + (cgSaPolPc[(self.mask([1]))] * aduePolVal[(self.mask([1]))] + cgSaPriPc[(self.mask([1]))]) * insuredSum[(self.mask([1]))] * policeActive[(self.mask([1]))]
        # PrInventPp = self.one()
        return prInventPp            
                      
    # VAL_NETP_FAC - durée restante mensuelle, à 0 si pas de paiement des primes
    def valNetpFac(self):
        # situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        # conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        # result = [(99 - (self.durationIf()/12))]
        # sinon = 0
        # valNetpFac = np.select(conditions,result,sinon)
        dureePayPrimes = self.p['POLDURP'][:,np.newaxis,np.newaxis] * self.one()
        maskDureeEq99 = dureePayPrimes == 99 
        masDureeNotEq99 = dureePayPrimes != 99
        
        ax = self.ax
        axp = self.axp
        policeActive = self.policeActive()
        
        valNetpFac = self.zero()
        # valNetpFac = self.ax() * self.policeActive()
        valNetpFac[maskDureeEq99] = np.maximum(ax[maskDureeEq99] * policeActive[maskDureeEq99],0)
        valNetpFac[masDureeNotEq99] = np.maximum(axp[masDureeNotEq99] * policeActive[masDureeNotEq99],0)
        
        # calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        durationIf = self.durationIf()
        policeActive = self.policeActive()
        valNetpFac[(self.mask([11]))] = (99 - (durationIf[(self.mask([11]))]/12))*policeActive[(self.mask([11]))]

        return valNetpFac
    
    # VAL_POL_FAC - durée restante mensuelle, ne dépend pas des primes
    def valPolFac(self):
        
        # valPolFac = self.ax()

        # valPolFac = self.ax()
        valPolFac = self.ax

        # calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        durationIf = self.durationIf()
        valPolFac[(self.mask([11]))] = (99 - (durationIf[(self.mask([11]))]/12))
        return valPolFac
    
    # VAL_ZILL_PP - valeur de zillmérisation    
    def valZillPP(self):
        
        
        self.p['POLDTDEB'] = pd.to_datetime(self.p['POLDTDEB'])
        self.p['ANDEBUT'] = self.p['POLDTDEB'].dt.year
        anDebut = self.p['ANDEBUT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        valZillPC = self.zero()
        # valZillPC = (5/100) * self.one()
        
        valZillPC[anDebut<2011] = (8/100) * self.one()[anDebut<2011]
        valZillPC[anDebut>=2011] = (5/100) * self.one()[anDebut>=2011]
        
        ValZillPP = np.minimum(valZillPC * self.prInventPP() * self.valNetpFac(), self.valSumAssd() - self.valNetpPP() + self.provGestPP())
        # ValZillPP = np.minimum(valZillPC * self.prInventPP() * self.valNetpFac(), self.insuredSum() - self.valNetpPP() + self.provGestPP())
        return ValZillPP
    
    # MATH_RES_BA - provision mathématique 
    def mathResBa(self):
        
        # pour la 11:
        # mathResBa = np.maximum(self.insuredSum() + self.valAccrbPP() + self.provGestPP() + self.valPrecPP() - self.valNetpPP() - self.valZillPP(), 0)
        
        # pour la 01:
        mathResBa = np.maximum(self.valSumAssd()  + self.valPrecPP() - self.valNetpPP() + self.provGestPP() - self.valZillPP(), 0)
        
        
        return mathResBa
    
# =============================================================================
    ### FRAIS -> INTEGRER PTF
# =============================================================================

    # Frais sur durée due la police
    def cgSaPolPc(self):
        # conditions = [(self.p['Age1AtEntry'] < 53), (self.p['Age1AtEntry'] < 70)]
        # result =[(0.25), (0.45)]
        # sinon = (0.9)
        # cgSaPolPc = np.select(conditions,result,sinon)[:,np.newaxis,np.newaxis] * self.one()
        
        
        cgSaPolPc = self.p['fraisGestDureePoliceSA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        return cgSaPolPc
    
    # Frais sur durée du paiement des primes
    def cgSaPriPc(self):
        # conditions = [(self.p['Age1AtEntry'] < 53), (self.p['Age1AtEntry'] < 70)]
        # result =[(0.35), (0.55)]
        # sinon = (1.2)
        # cgSaPriPc = np.select(conditions,result,sinon)[:,np.newaxis,np.newaxis] * self.one()
        
        
        cgSaPriPc = self.p['fraisGestDureePrimesSA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
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
        mask = calendarMonth == 1
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
    
        return ridercOutgo * self.payPrimes()

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

# définition de pol
pol = VE()

# police force 3
# pol.ids([731902]) okay
# pol.ids([818202]) okay
# pol.ids([2211301]) okay
# pol.ids([1132602]) okay
# pol.ids([1132701]) okay
# pol.ids([889603]) okay
# pol.ids([732001])


# police unique
# pol.ids([743801])


# échantillon force F1VE01
# pol.ids([71601, 71801, 236605, 294101, 350001, 375801, 399202, 743801, 1847802, 1847803])

# échantillon force F1VE02
# pol.ids([101203, 895602, 2055601, 2056801, 2085801, 2085901])

# échantillon force F1VE03
# pol.ids([2168202, 2172401, 2178001])

# échantillon force F1VE04
# pol.ids([572405, 572503, 731902, 732001, 818202, 889603, 1132602, 1132701, 2211301])

# selection de la modalité
# pol.mod([1])

print("Class VE--- %s sec" %'%.2f'%  (time.time() - start_time))





x = pol.p
x.to_excel(path+'/zFT/ptf.xlsx')
monCas = pol.numberSurrenders()
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zFT/check.csv',header=False)
