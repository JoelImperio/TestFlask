from Portefeuille import Portfolio
from Parametres import allRuns
import numpy as np
import pandas as pd
import time
import os, os.path
#from MyPyliferisk import mortalitytables
from MyPyliferisk.mortalitytables import *
#path = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()




# =============================================================================
# Création de la classe Sérénité
# =============================================================================
tableFemmes = 'EKF05i'
tableHommes = 'EKM05i'
    
class VE(Portfolio):
    mods=[11]

    lapseTiming = 0.5
    minResPp = 0
    aidsDefRes = 0
    valZillPc = (5/100)
            
    tableFemmes = 'EKF05i'
    tableHommes = 'EKM05i'
    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopNoSaving()
        self.lapse()
         
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
        # mylapse=1-(1-mylapse)**(1/frac)
        mylapse=1-(1-mylapse)**(1/12)
        
        mylapse= self.isLapse()*mylapse
        
        return mylapse
     
    def loopNoSaving(self):
        
        lapseTiming = 0.5
        
        nbrPolIf=self.one()
        nbrDeath=self.zero()
        nbrSurrender=self.zero()
        nbrMaturities=self.zero()
        nbrPolIfSM=self.zero()
        
        matRate=self.zero()
        polTermM=self.polTermM()
        
        matRate[polTermM + 1==self.durationIf()]=1
        
        qxy=self.qxyExpMens()
        lapse=self.lapse()
           
        for i in range(1,self.shape[1]):
            
            nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
            nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]
            
            nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapse[:,i,:]*(1-lapseTiming)))
            
            nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxy[:,i,:]*lapseTiming))

            nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrMaturities[:,i,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]

#Définition des variables récursives
        
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
# --- Début des variables du produit
# =============================================================================

# =============================================================================
# ---Calcul de surrOutgo
# =============================================================================

    def insuredSum(self):
        sumAssdPp = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        return sumAssdPp
                   
    def VAL_ACCRB_PP(self):
        valAccrbPp = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]*self.one()
        return valAccrbPp
    
    def ADUE_VAL(self):
        polTerm = self.p['POLDURC'].to_numpy()[:,np.newaxis,np.newaxis]
        adueVal = polTerm - ((self.durationIf()+1)/12)
        adueVal = np.floor(adueVal)
        return adueVal

    def PMG_SA_PC(self):
        pmgSaPc = self.fraisGestion() * self.VAL_NETP_FAC()
        return pmgSaPc
       
    def PROV_GEST_PP(self):
        provGestPp = self.PMG_SA_PC()/100 * (self.insuredSum() + self.VAL_ACCRB_PP()) \
        - self.VAL_NETP_FAC() * (self.PR_INVENT_PP() - self.purePremium())
        return provGestPp
    
    def VAL_PREC_PP(self):
        agelimite=(self.age()<=85)
        # Calcul du risque en cours
        riderIncPP=self.primeTotaleMensuelle()*self.isPremPay()*agelimite
        riderIncPP2=self.primeTotaleMensuelle()*agelimite
        precPP=self.zero()
        frek=self.frac()
     
        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
   
        return precPP
    
    def purePremium(self):
        purePremium =  self.insuredSum() / 99
        return purePremium
    
    def primeTotale(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotale = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] / frac * self.isPremPay()
        return primeTotale 
    
    def primeTotaleMensuelle(self):
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        primeTotaleMensuelle = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis] *self.one() / frac
        return primeTotaleMensuelle 

    def VAL_NETP_PP(self):
        ValNetpPp = self.purePremium() * self.VAL_NETP_FAC()
        return ValNetpPp
        
    def fraisGestion(self):
        fraisGestion = self.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        return fraisGestion
    
    def PR_INVENT_PP(self):
        PrInventPp = (self.purePremium() + (self.fraisGestion() * self.insuredSum()) + self.fraisGestion() * self.insuredSum())/100 
        return PrInventPp
          
    def VAL_NETP_FAC(self):
        valNetpFac = 99 - (self.durationIf()/12)
        return valNetpFac
        
    def valZill(self):
        valZillPc = self.valZillPc * self.one()
        ValZillPp = np.minimum(valZillPc * self.PR_INVENT_PP() * self.VAL_NETP_FAC(), self.insuredSum() - self.VAL_NETP_PP() + self.PROV_GEST_PP())
        return ValZillPp

    def MATH_RES_BA(self):
        mathResBa = np.maximum(self.insuredSum() + self.VAL_ACCRB_PP() + self.PROV_GEST_PP() + self.VAL_PREC_PP() - self.VAL_NETP_PP() - self.valZill(), self.minResPp)
        return mathResBa

    def numberSurrenders(self):
        noSurrs = self.nbrPolIfSM * self.lapse() * (1-self.lapseTiming*self.qxExpMens())
        return noSurrs

# =============================================================================
# ---Calcul de DEATH OUTGO
# =============================================================================    
    
    def numberDeaths(self):
        noDeaths= self.qxExpMens() * self.nbrPolIfSM *(1 - self.lapse()*self.lapseTiming)
        return noDeaths
    
    def deathBenefit(self):
        capital = self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]
        primetot = self.p['POLPRTOT'].to_numpy()[:,np.newaxis,np.newaxis]     
        frac = self.p['PMBFRACT'].to_numpy()[:,np.newaxis,np.newaxis]
        pbAcq = self.p['PMBPBEN'].to_numpy()[:,np.newaxis,np.newaxis]
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        durationif = self.durationIf()
        
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result =[(primetot/frac)]
        sinon = 0
        deathBenPPinitial = np.select(conditions,result,sinon)
        deathBenPP1 = self.zero()
        deathBenPP2 = self.zero()
        deathBenPP = self.zero()
        durationif12plus = self.zero()
        durationif13less = self.zero()
        deathBenPP1[:,0,:] = deathBenPPinitial[:,0,:]
        
        conditions = [(durationif>12)]
        result =[(1)]
        sinon = 0
        durationif12plus = np.select(conditions,result,sinon)
        
        conditions = [(durationif<13)]
        result =[(1)]
        sinon = 0
        durationif13less = np.select(conditions,result,sinon) 
        
        # for i in range(0,self.shape[1]):                                                                                 

        #     # deathBenPP1[:,i,:] = (deathBenPP1[:,i-1,:] + deathBenPPinitial[:,0,:]) * durationif13less[:,i,:]
        #     deathBenPP1[:,i,:] = (durationif[:,i,:] * deathBenPPinitial[:,0,:]) * durationif13less[:,i,:]
        #     deathBenPP2[:,i,:] = (capital[:,0,:] + pbAcq[:,0,:]) * durationif12plus[:,i,:]
        # deathBenPP = deathBenPP1 + deathBenPP2
        
        deathBenPP1[:,:,:] = (durationif[:,:,:] * deathBenPPinitial[:,:,:]) * durationif13less[:,:,:]
        deathBenPP2[:,:,:] = (capital[:,:,:] + pbAcq[:,:,:]) * durationif12plus[:,:,:]
        deathBenPP = deathBenPP1 + deathBenPP2
        
        return deathBenPP

# =============================================================================
# --- Composants de totalExpense
# =============================================================================
    def initialExpenses(self):
        initialExpenses = self.zero()
        return initialExpenses
      
    def renewableExpenses(self):
        reserveExpenses = (0.328733769/1200)
        fixedAnnualExpense = (120/12)
        inflation = self.inlfation()
        renewableExpenses = (self.nbrPolIfSM() * inflation * fixedAnnualExpense + self.adjustedMathReserve() * reserveExpenses)
        return renewableExpenses
    
    def adjustedMathReserve(self):
        adjustedMathReserve = np.maximum(0, (self.F_MATH_RES_IF() + self.RFIN_ANN_NC() + self.ridercOutgo() + self.PPURE_ENC()))
        return adjustedMathReserve
    
    def F_MATH_RES_IF(self):
        fMathResIf = self.MATH_RES_BA() * self.nbrPolIf
        return fMathResIf
    
    def RFIN_ANN_NC(self):
        # c'est le bordel
        rfinAnnNc = self.one()
        return rfinAnnNc
    
    def PPURE_ENC(self):
        # Complètement faux, Prophet divise la prime pure mensuelle par le
        # fractionnemenet et multiplie le résultat par les inforce...
        # alors que la prime pure fractionnée est déjà calculée ailleurs
        ppureEnc = pol.nbrPolIfSM * pol.purePremium() / pol.frac() * pol.isPremPay()
        # Correct:
        # ppureEnc = pol.nbrPolIfSM * pol.purePremium() * (12/pol.frac()) * pol.isPremPay()
        return ppureEnc
        
# =============================================================================
# --- Composants de totalPrest    
# =============================================================================
    def surrOutgo(self):
        surrOutgo = self.MATH_RES_BA() * self.numberSurrenders()
        return surrOutgo
    
    def deathOutgo(self):
        deathOutgo = self.deathBenefit() * self.numberDeaths()
        return deathOutgo
    
    def ridercOutgo(self):
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        conditions = [(self.age() <= 85) & (situation != 4) & (situation != 8) & (situation != 9)]
        # Attention:
        result =[(self.totalPremium() * self.dcAccident())]
        # Faux, il ne faut pas prendre la prime totale mais la prime accident
        sinon = 0
        ridercOutgo = np.select(conditions,result,sinon)
        return ridercOutgo
    
# =============================================================================
# --- Calcul des composants du BEL 
# =============================================================================
#Retourne les primes totales perçues
    def totalPremium(self):
        premInc = self.p['POLPRTOT'][:,np.newaxis,np.newaxis]/self.frac()
        situation = self.p['POLSIT'][:,np.newaxis,np.newaxis]
        
        conditions = [(situation != 4) & (situation != 8) & (situation != 9)]
        result =[(premInc*self.nbrPolIfSM*self.isPremPay())]
        sinon = 0
        prem = np.select(conditions,result,sinon)
        return prem

#Retourne le total des prestations payés 
    def totalPrest(self):
        return self.deathOutgo() + self.ridercOutgo() + self.surrOutgo()

#Retourne le total des commissions payées
    def totalCommissions(self):
        return self.totalPremium() * self.commissions()

#Retourne les dépense totales 
    def totalExpense(self):
        return self.initialExpenses() + self.renewableExpenses()



# =============================================================================
# --- Calcul du BEL   
# =============================================================================
    def BEL(self):
        
        interestRates=1+self.rate()       
        premium=self.totalPremium()
        claim=self.totalPrest()
        expense=self.totalExpense()
        commission=self.totalCommissions()
        
        bel=self.zero()
              
        for t in range(1,self.shape[1]+1):
            bel[:,-t,:]=(bel[:,-t+1,:]+claim[:,-t+1,:]+expense[:,-t+1,:]+commission[:,-t+1,:]-premium[:,-t+1,:])/interestRates[:,-t+1,:]
        return bel
    
    
    
pol = VE()

pol.ids([1713905])

portefeuille = pol.p
adue = pol.ADUE_VAL()
lapse = pol.lapse()
ptf = pol.p
inforce = pol.nbrPolIf
inforceM = pol.nbrPolIfSM
maturites = pol.nbrMaturities
deaths = pol.nbrDeath
surrender = pol.nbrSurrender

test = pol.PPURE_ENC()



a = pol.PR_INVENT_PP()
b = pol.VAL_NETP_PP()
c = pol.VAL_NETP_FAC()
d = pol.PROV_GEST_PP()

valZillPc = pol.valZillPc * pol.one() 
ValZillPp = np.minimum(valZillPc * pol.PR_INVENT_PP() * pol.VAL_NETP_FAC(), pol.insuredSum() - pol.VAL_NETP_PP() + pol.PROV_GEST_PP())
