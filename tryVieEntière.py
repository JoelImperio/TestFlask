from Portefeuille import Portfolio
from Parametres import allRuns
import numpy as np
import pandas as pd
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()

# =============================================================================
#   Création de la classe Sérénité
# =============================================================================
  
class VE(Portfolio):
    mods=[1, 11]

    # LapseTimine à 0.5 pour les VE
    lapseTiming = 0.5
    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
    
    # L'update contient les self retournés des loop  
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopVE()
        self.commutations()
        self.reserveForExp()
    
    # Fonction modifiée des lapse car VE lapsent mensuellement
    def isLapse(self):
        lapse = self.zero()
        check1 = (self.frac() * (self.durationIf()+12)/12)
        check2 = np.floor((self.frac()*(self.durationIf()+12)/12))
        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [lapse[:,:,:]==0, lapse[:,:,:]==0]
        myLapse=np.select(condlist, choicelist)
        # Le premier mois il n'y a pas de payement car la prime est payé en début de mois et les date de calcul sont en fin de mois
        myLapse[:,0,:] = 0
        return myLapse
    
    # !! Fonction mondifiée des lapse car VE lapsent mensuellement, a effacer pour corriger 
    # Par contre ne pas oublier le mask99 pour la durée
    def lapse(self):
        
        # masque pour la durée de 99 ans
        mask99 = (self.durationIf() <= 99*12)
        
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
        
        mylapse= self.isLapse() * mylapse * mask99
        
        return mylapse
     
    # Loop qui calcule les maturités, inforce annuels et mensuels, nombre de morts, nombre de surrenders.    
    def loopVE(self):
        
        # Masque durée projections
        mask98 = (self.durationIf() <= 98*12+1)
        
        # Vecteur mise à zéro
        nbrPolIf = self.one()
        nbrDeath = self.zero()
        nbrSurrender = self.zero()
        nbrPolIfSM = self.zero()
        matRate = self.zero()
        
        # Déclaration de certains vecteurs
        polTermM = self.polTermM()
        matRate[polTermM + 1==self.durationIf()]=1
        qxy = self.qxyExpMens()
        lapse = self.lapse()
         
        # Début du loop
        for i in range(1,self.shape[1]):
            nbrPolIfSM[:,i,:] = nbrPolIf[:,i-1,:] * mask98[:,i,:]
            nbrDeath[:,i,:] = nbrPolIfSM[:,i,:] * qxy[:,i,:] * (1-(lapse[:,i,:] * (1-self.lapseTiming))) 
            nbrSurrender[:,i,:] = nbrPolIfSM[:,i,:] * lapse[:,i,:] * (1-(qxy[:,i,:] * self.lapseTiming))
            nbrPolIf[:,i,:] = nbrPolIf[:,i-1,:] - nbrDeath[:,i,:] - nbrSurrender[:,i,:]

        #Nombre de polices actives                                 
        self.nbrPolIf = nbrPolIf
        #Nombre de police actives en déduisant les échéances du mois
        self.nbrPolIfSM = nbrPolIfSM
        #Nombre de décès
        self.nbrDeath = nbrDeath 
        #Nombre d'annulation de contrat
        self.nbrSurrender = nbrSurrender * mask98

    # Fonction qui sert à déterminer si une police est active ou non par rapport à sa situation, peut-être doublon
    def policeActive(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis] * self.one()
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result =[(1)]
        sinon = 0
        policeActive = np.select(conditions,result,sinon)
        return policeActive
    
    # Fonction qui sert à déterminer à partir de quand les primes ne sont plus payées (POLDURP)
    def payPrimes(self):
        durationIf = self.durationIf()
        payPrimes = self.one()
        moisPaiement = (self.p['POLDURP'].to_numpy() * 12 )[:,np.newaxis,np.newaxis] * self.one()
        conditions = [(durationIf <= moisPaiement)]
        result =[(1)]
        sinon = 0
        payPrimes = np.select(conditions,result,sinon)
        return payPrimes
    
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
   
# =============================================================================
    ### FONCTIONS A REMONTER
# =============================================================================
 
    # Fonction piquée dans les épargnes
    def allocMonths(self):
        calendarMonth=np.arange(start=self.p['DateCalcul'].dt.month.values[0].astype(int),stop=(self.shape[1]+self.p['DateCalcul'].dt.month.values[0].astype(int)))
        calendarMonth=calendarMonth%12 + 1
        calendarMonth=calendarMonth[np.newaxis,:,np.newaxis]*self.one()        
        mask = calendarMonth == 1
        return mask*1

    # Fonction prise des épargnes qui n'avait pas été remontée  
    def isActive(self):
        moisRestant = self.p['residualTermM'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        increment = np.cumsum(self.one(), axis = 1)-1
        mask = moisRestant >= increment
        return mask
    
    # Piqué dans les épargnes
    def mUfii(self):
        rate = (1+self.rate())**12 - 1
        rate = np.round(rate, decimals = 6)
        rate = (1+rate)**(1/12) - 1
        return rate
      
# =============================================================================
    ### CALCUL DES PRIMES
# =============================================================================

    # Frais sur durée due la police
    def fraisGestDureePoliceSA(self):
        return self.p['fraisGestDureePoliceSA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
    
    # Frais sur durée du paiement des primes
    def fraisGestDureePrimesSA(self):
        return self.p['fraisGestDureePrimesSA'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
      
    # Primes brutes mensuelles (ne dépend pas de isprempay)  
    def primeTotaleMensuelle(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotale = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        return primeTotale / frac
    
    # !! Retourne les primes totales perçues, fonction modifiée à cause de la complémentaire à déduire, faux
    # Sérénité:
        # Au 85ème  anniversaire de l’assuré, lorsque la garantie complémentaire « Accident » cesse, 
        # la prime total n’est pas réduite. L’assuré continue de régler le même montant de prime.  
    # Force 3:
        # Après le 85ème anniversaire de l’assuré, Império ne verse que le capital de base, 
        # quelque soit la cause de l’accident. La prime reste constante : 
        # la surprime qui en résulte sert de marge de sécurité pour les âges élevés.
    def totalPremium(self):
        agelimite = (self.age()>85) 
        mask1 = self.p['PMBMOD'].isin([1])
        prTot = self.p['POLPRTOT'][:,np.newaxis,np.newaxis]
        prCompl = self.p['POLPRCPL3'][:,np.newaxis,np.newaxis]
        # !! La prime complémentaire est déduite après 85 ans pour la mod1 mais pas pour la 11; elle ne doit pas être déduite
        premInc = prTot / self.frac()
        premInc[mask1] = (prTot[mask1] - (prCompl[mask1] * agelimite[mask1])) / self.frac()[mask1]
        prem = premInc * self.nbrPolIfSM * self.isPremPay() * self.indexation()
        return prem * self.payPrimes() 
    
    # !! Comportement bizarre en fin de projection répliqué
    def qxyExpMens(self):
        maskotte1 = self.durationIf() > 98*12
        maskotte2 = self.durationIf() <= 99*12
        mask = maskotte1 & maskotte2
        mask121 = (self.age() <= 121)
        qx = self.qxExpMens(ass=1)
        qy = self.qxExpMens(ass=2)
        return (qx + qy - qx * qy) * mask121 + mask
    
    # SUM_ASSD_PP - capital de la police
    def insuredSum(self):
        mask99 = (self.durationIf() <= 99*12)
        sumAssdPp = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one() 
        return sumAssdPp * mask99
    
    # VAL_SUM_ASSD - Capital multiplié par les Ax
    def valSumAssd(self): 
        valSumAssd = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one() 
        return valSumAssd * self.Ax

    # PR_PURE_PP - Prime pure calcul éronné pour la mod11
    def purePremium(self):
        purePremium = self.insuredSum() / self.axInitPrimes * self.policeActive() * self.payPrimes()
        
        # !! calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        mask99 = (self.durationIf() <= 99*12)
        insuredSum = self.insuredSum()
        purePremium[(self.mask([11])) & mask99] = insuredSum[(self.mask([11])) & mask99] / 99
        return purePremium
    
    # PR_INVENT_PP prime d'inventaire (prime pure + les frais de gestion sur somme assurée)
    def prInventPP(self):
        purePremium = self.purePremium()
        cgSaPolPc = self.fraisGestDureePoliceSA()
        cgSaPriPc = self.fraisGestDureePrimesSA()
        insuredSum = self.insuredSum()
        policeActive = self.policeActive()
        aduePolVal = self.aduePolVal
        mask99 = (self.durationIf() <= 99*12)
        prInventPp = purePremium + (cgSaPolPc * aduePolVal + cgSaPriPc) * insuredSum * policeActive
        
        # !! Le calcul pour la 1 devrait être commun à la 11 et la 1
        prInventPp[(self.mask([11]))] = purePremium[(self.mask([11]))] + (cgSaPolPc[(self.mask([11]))] + cgSaPriPc[(self.mask([11]))]) * insuredSum[(self.mask([11]))] * policeActive[(self.mask([11]))] * mask99[(self.mask([11]))]
        return prInventPp            
                      
# =============================================================================
    ### CALCUL DES CLAIMS   
# =============================================================================

    # DEATH_BEN_PP - calcul du death benefit
    def deathBenefit(self):
        
        capital = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]    
        frac = 12 / self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        frac = 12 / self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        pbAcq = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]
        durationif = self.durationIf()  
        isPremPay = self.isPremPay()
        
        conditions = [durationif[:,0,:] != 1, durationif[:,0,:] == 1]
        result =[np.ceil(durationif[:,0,:]/frac[:,0,:]), 1]
        isPremPay[:,0,:] = np.select(conditions,result)
        
        premiumsPaid = isPremPay * self.p['POLPRTOT'][:,np.newaxis,np.newaxis] / self.frac()           
        cumulatedPremiums = self.zero()
        cumulatedPremiums = np.cumsum(premiumsPaid, axis=1)      
        
        conditions = [(durationif>12)]
        result = [(0)]
        sinon = 1
        deathBenPP1 = np.select(conditions,result,sinon) * cumulatedPremiums
        
        conditions = [(durationif>12)]
        result = [(1)]
        sinon = 0
        durationif12plus = np.select(conditions,result,sinon)
        
        deathBenPP2 = (capital + pbAcq) * durationif12plus  
        
        return deathBenPP1 + deathBenPP2
    
    # SURRENDER_OUTGO - Claims réductions
    def surrender(self):
        conditions = [(self.durationIf()>36)]
        result =[(self.mathResBa() * self.nbrSurrender)]
        sinon = 0
        surrOutgo = np.select(conditions,result,sinon)
        return surrOutgo
    
    # DEATH_OUTGO - Claims garantie principale
    def claimPrincipal(self):
        return self.deathBenefit() * self.nbrDeath
    
    # RIDERC_OUTGO - Claims complémentaires
    def claimCompl(self):
    
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
        
        ridercOutgo[mask_infeqf85] = cpl3[mask_infeqf85] * dcAccident[mask_infeqf85] * isPremPay[mask_infeqf85] * nbrPolIfSM[mask_infeqf85]
        ridercOutgo[mask_sup85] = zero[mask_sup85] 
        
        # !! Faux, à enlever, il ne faut pas prendre le totalPremium mais la cpl3
        ridercOutgo[(self.mask([11])) & mask_infeqf85] = totalPremium[(self.mask([11])) & mask_infeqf85] * dcAccident[(self.mask([11])) & mask_infeqf85]
        ridercOutgo[(self.mask([11])) & mask_sup85] = zero[(self.mask([11])) & mask_sup85] 

        return ridercOutgo * self.payPrimes()

    # MATH_RES_BA - provision mathématique 
    def mathResBa(self):
        mathResBa = self.zero()
        mask11 = self.p['PMBMOD'].isin([11])
        mask01 = self.p['PMBMOD'].isin([1])
        
        # pour la 11:
        mathResBa[mask11] = np.maximum(self.insuredSum()[mask11] + self.valPrecPP()[mask11] - self.valNetpPP()[mask11]  + self.provGestPP()[mask11]   - self.valZillPP()[mask11] + self.valAccrbPP()[mask11], 0)
        
        # pour la 01:
        mathResBa[mask01] = np.maximum(self.valSumAssd()[mask01] + self.valPrecPP()[mask01] - self.valNetpPP()[mask01] + self.provGestPP()[mask01] - self.valZillPP()[mask01], 0)
        return mathResBa
    
    # VAL_ZILL_PP - valeur de zillmérisation    
    def valZillPP(self):
        valZillPC = self.p['tauxZill'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        ValZillPP = np.minimum(valZillPC * self.prInventPP() * self.valNetpFac(), self.valSumAssd() - self.valNetpPP() + self.provGestPP())
        ValZillPP[(self.mask([11]))] = np.minimum(valZillPC[(self.mask([11]))] * self.prInventPP()[(self.mask([11]))] * self.valNetpFac()[(self.mask([11]))], self.insuredSum()[(self.mask([11]))] - self.valNetpPP()[(self.mask([11]))] + self.provGestPP()[(self.mask([11]))])
        return ValZillPP
    
    # PROV_GEST_PP - Provision de gestion par police, quelle logique
    def provGestPP(self):
        return self.pmgSaPc() * (self.insuredSum() + self.valAccrbPP()) - self.valNetpFac() * (self.prInventPP() - self.purePremium())
    
    # PMG_SA_PC - traitement des frais pour provGestPP
    def pmgSaPc(self):
        return self.fraisGestDureePrimesSA() * self.valNetpFac() + self.fraisGestDureePoliceSA() * self.valPolFac()
    
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
        
        # !! Faux, à enlever, il ne faut pas prendre le totalPremium mais la cpl3
        riderIncPP[(self.mask([11]))] = primeTotaleMensuelle[(self.mask([11]))] * isPremPay[(self.mask([11]))] * agelimite[(self.mask([11]))] 
        riderIncPP2[(self.mask([11]))] = primeTotaleMensuelle[(self.mask([11]))] * agelimite[(self.mask([11]))] 

        precPPbis=self.zero()
        frek=self.frac()
        
        for i in range(1,self.shape[1]):
            precPPbis[:,i,:] = precPPbis[:,i-1,:] + riderIncPP[:,i,:] - ((frek[:,i,:] / 12) * riderIncPP2[:,i,:])
        
        return precPPbis * self.isActive() 
    
    # VAL_POL_FAC - annuité qui dépend de la durée du contrat (faux pour sérénité)
    def valPolFac(self):
        valPolFac = self.ax
        # !! calcul erronné pour la modalité 11, à enlever une fois PGG répliquée:
        durationIf = self.durationIf()
        valPolFac[(self.mask([11]))] = (99 - (durationIf[(self.mask([11]))]/12))
        return valPolFac
    
    # VAL_NETP_PP valeur des primes nettes
    def valNetpPP(self):
        return self.purePremium() * self.valNetpFac()
    
    # VAL_NETP_FAC - annuité qui dépend de la durée de paiemnet des primes (ax, axp, faux pour sérénité)
    def valNetpFac(self):
        dureePayPrimes = self.p['POLDURP'][:,np.newaxis,np.newaxis] * self.one()
        maskDureeEq99 = dureePayPrimes == 99 
        masDureeNotEq99 = dureePayPrimes != 99
        
        ax = self.ax
        axp = self.axp
        policeActive = self.policeActive()
        
        valNetpFac = self.zero()
        valNetpFac[maskDureeEq99] = np.maximum(ax[maskDureeEq99] * policeActive[maskDureeEq99],0)
        valNetpFac[masDureeNotEq99] = np.maximum(axp[masDureeNotEq99] * policeActive[masDureeNotEq99],0)
        
        # !! calcul erronnée pour la modalité 11, à enlever une fois PGG répliquée:
        mask99 = (self.durationIf() <= 99*12)
        durationIf = self.durationIf()
        policeActive = self.policeActive()
        valNetpFac[(self.mask([11])) & mask99] = (99 - (durationIf[(self.mask([11])) & mask99]/12))*policeActive[(self.mask([11])) & mask99]

        return valNetpFac
    
    # VAL_ACCRB_PP - valeur de la PB acquise en début de projection               
    def valAccrbPP(self):
        valAccrbPp = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        return valAccrbPp
    
# =============================================================================
    ### CALCUL DES EXPENSES
# =============================================================================

    # F_MATH_RES_IF - prov math actualisée avec les inforce
    def fMathResIf(self):
        fMathResIf = self.mathResBa() * self.nbrPolIf
        return fMathResIf    
   
    def unitExpense(self):
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:] = 0
        coutParPolice=self.fraisGestion()
        cost=coutParPolice*inflation*self.nbrPolIfSM
        return cost

    #  Calcul des réserve mathématiques adjustées
    def reserveForExp(self):
        
        # déclaration des variables utilisées
        totExp = self.zero()
        rfinAnn = self.zero()
        adjMathRes2 = self.zero()
        resFinMois = self.zero()
        provMathAj = self.zero()
        oExp = self.zero()
        oTaxblInc = self.zero()
        totCom = self.totalCommissions()
        fMathResIf = self.fMathResIf()
        riderCoutgo = self.claimCompl()
        premInc = self.totalPremium()
        provMathIf = self.mathResBa() * self.nbrPolIf
        mUfii = self.mUfii()
        monthPb = self.one() - self.allocMonths()
        totIntCred = self.totalIntCred() 
        premInvest = self.purePremium() * self.nbrPolIfSM / self.frac() * self.isPremPay() * self.policeActive()
        unitExp = self.unitExpense() 
        txReserve = self.fraisGestionPlacement()
        
        # calcul des exceptions
        provMathAj[:,0,:] = premInc[:,0,:] - totExp[:,0,:] - riderCoutgo[:,0,:]
        
        # Loop des expense
        for i in range(1,self.shape[1]):
            adjMathRes2[:,i,:] = np.maximum(0, fMathResIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:])
            totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:] 
            oExp[:,i,:] = totExp[:,i,:] + totCom[:,i,:]
            provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - oExp[:,i,:]
            oTaxblInc[:,i,:] = provMathAj[:,i,:] * mUfii[:,i,:]
            resFinMois[:,i,:] = oTaxblInc[:,i,:] - totIntCred[:,i,:]
            rfinAnn[:,i,:] = (rfinAnn[:,i-1,:] + resFinMois[:,i,:]) * monthPb[:,i,:] 

   #Définition des variables récursives (celles inutiles pour runner le code sont commentées)
        # Résultat financier en fin de mois non constaté
        # self.resFinMois = resFinMois
        # Résultat de l'année en cours non constaté
        # self.rfinAnn = rfinAnn
        # Reserves mathématiques ajustées pour calculer les expenses
        self.adjMathRes2 = adjMathRes2
        # Provisions mathématiques ajustées
        # self.provMathAj = provMathAj
        # Total des expenses
        # self.totExp = totExp

    def reserveExpense(self):
        reserveExpense = self.adjMathRes2 * self.fraisGestionPlacement()
        return reserveExpense
    
    # PPURE_ENC
    def ppureEnc(self):
        ppureEnc = self.nbrPolIfSM * self.purePremium() / self.frac() * self.isPremPay()
        return ppureEnc
        
    # Total des intérêts crédités
    def totalIntCred(self):
        
        # Intérêts crédités sur zillmérisation
        valZillIf = self.valZillPP() * self.nbrPolIf
        intCredZill = (self.txInt()-1) * -1 * np.roll(valZillIf, 1, axis=1)
        
        # Intérêts techniques crédités
        intCredT = (self.txInt()-1) * self.provTechAj()
        
        # Intérêts crédités sur PMG
        provGestIf = self.provGestPP() * self.nbrPolIf
        intCredPgm = (self.txInt()-1) * np.roll(provGestIf, 1, axis=1)
        
        # totalIntCred = self.intCredT() + self.intCredZill() + self.intCredPgm()
        totalIntCred = intCredT + intCredZill + intCredPgm
        # ? Doivent-ils être à zéro pour la 11? Positifs pour la 1?
        totalIntCred[(self.mask([11]))] = self.zero()[(self.mask([11]))]
        return totalIntCred
      
    # Provision technique ajustée
    def provTechAj(self):
        
        # Provision technique par polices
        provTechPP = self.mathResBa() - self.provGestPP() - self.valPrecPP() + self.valZillPP()
        
        # calcul des provisions techniques en cours
        provTechIf = provTechPP * self.nbrPolIf 
        provTechIf = np.roll(provTechIf, 1, axis = 1)
        provTechIf[:,0,:] = 0
        provTechAj = provTechIf + self.ppureEnc() - self.claimCompl()
        return provTechAj
   
# Retourne les primes totales perçues
    # def totalPremium(self):
        
#Retourne le total des prestations payés 
    # def totalClaim(self):
        
#Retourne le total des commissions payées
    # def totalCommissions(self):

#Retourne les dépense totales 
    # def totalExpense(self):

# définition de pol
pol = VE()


# police unique
# pol.ids([2314102])

# valZillPC = pol.p['tauxZill'].to_numpy()[:,np.newaxis,np.newaxis] * pol.one()

# échantillon force F1VE01
# pol.ids([71601, 71801, 236605, 294101, 350001, 375801, 399202, 743801, 1847802, 1847803])

# échantillon force F1VE02
# pol.ids([101203, 895602, 2055601, 2056801, 2085801, 2085901])

# échantillon force F1VE03
# pol.ids([2168202, 2172401, 2178001])

# échantillon force F1VE04
# pol.ids([572405, 572503, 731902, 732001, 818202, 889603, 1132602, 1132701, 2211301])

# selection de la modalité
# pol.mod([11])



print("Class VE--- %s sec" %'%.2f'%  (time.time() - start_time))


x = pol.p
x.to_excel(path+'/zFT/ptf.xlsx')
monCas = pol.totalPremium()
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zFT/check.csv',header=False)
