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
class TEMP(Portfolio):
    # mods=[3]
    modHeads = [3],1
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
        






    # Modalité 28 
class EPP28(Portfolio):
    mods=[28]
    addSumAssuree = 7500
    protectionAvCap = 25000
    ageLimite = 75
    premiumDCmaladie = 48

    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)


#Permet de relancer l'update() en intégrant des methodes de la sous-classe (ICI la loop inforce possède la possibilité de réduction)
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopSaving()
        self.loopReduction()
        self.epargnAcqu()
        self.pbAcqu()
        self.matOutgo()
        self.reserveForExp()


# Créer un vecteur de temporel en année depuis le début de la projection qui dépend du duration if
    def time(self):
        
        durif = self.p['DurationIfInitial'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()-1
        durif = np.remainder(durif, 12)
        increment = np.cumsum(self.one(), axis = 1) -1 + durif
        increment = increment/12
        increment = np.floor(increment)
        
        return increment
    
    
# Créer un vecteur correspondans a calendar_month dans prophet (le mois de la projection)
    def calendarMonth(self):
        
        increment = np.cumsum(self.one(), axis = 1) -2
        increment = increment%12 +1

        return increment
    
    
    
    # Créer un vecteur de 1 et 0 pour connaître quand est-ce que le résultat annuel se remet à 0
    def rfinMonth(self):
        calendarMonth = self.calendarMonth()
        calendarMonth[calendarMonth==12]=0
        calendarMonth[calendarMonth!=0]=1
        return calendarMonth
    
    
# Ici se trouve la projection des primes dans le futur en tenant compte de l'indexation
    def premIndex(self):
        
        txIndex = (self.p['POLINDEX'].to_numpy()[:,np.newaxis,np.newaxis]/100) * self.one()
       
        # Les primes sont forcées à 0 lorsque la police est réduite
        mask = (self.p['POLSIT']==9)|(self.p['POLSIT']==4)|(self.p['PMBFRACT']==0)|(self.p['PMBFRACT']==5)
        premAnn = self.p['POLPRTOT'] * (1-mask)
        premAnn = premAnn.to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        premIndex = premAnn * (1 + txIndex)**self.time()
        
        return  premIndex



#  Vecteur des primes total encourue inforce
    def totalPremium(self):
        
        totPrem = self.isPremPay() * self.premIndex() * self.nbrPolIfSM/self.frac()
        
        return totPrem


# Calcul de la prime pure annuelle  
    def ppurePP(self):
        
       #  Condition qui met des primes à 0 pour des fractionnements 5 ou 0 et polices réduite
        mask = (self.p['POLSIT']==9)|(self.p['POLSIT']==4)|(self.p['PMBFRACT']==0)|(self.p['PMBFRACT']==5)
        premRider = (self.p['POLPRCPL9']) * (1-mask)
        premRider = premRider.to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        # Determine les frais d'acquisition en fonction de l'année du contrat (A CHANGER CAR ON AURA SUREMENT DES CHGT SUR 1 2 ou 3 ANS pour d'autres polices)
        acquisitionLoading = (self.durationIf()<=12) * self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        annPrem = self.premIndex()
        gestionLoading = self.p['gestionLoading'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        ppure = (annPrem -  premRider)*(1-gestionLoading -acquisitionLoading )
        return ppure
    
    
#  calcul de la prime encaissée investie par police
    def prEncInvPP(self): 
        return self.isPremPay() * self.ppurePP()/self.frac()


#  taux d'intêret mensualisé
    def txInt(self):
        txInteret = ((1+self.p['POLINTERG']/100)**(1/12)).to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        return txInteret



  # calcul de l'épargne acquise par police hors PB
    def epargAcqu(self):
        
        initEpargne = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]
        epargnAcquPP = self.zero()
        epargnAcquPP[:,0,:] = initEpargne
        prEncInv = self.prEncInvPP()
    # taux interet mensualisé
        txInteret = self.txInt()
        
    # loop de l'épargne acquise par police, (epargne acquise t-1 + prime investie capitalisé au taux d'intêret)
        for i in range(1,self.shape[1]):
        
            epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]
            
        return epargnAcquPP
    
    
    
#  PB acquise depuis le début du contrat
    def pbAcqu(self):
        
        pupBBenPP = self.zero()
        initPB = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pupBBenPP[:,0,:] = initPB
        pbAcquAVPUP = self.zero()
        pbAcquAPPUP =self.zero()
        
        # taux interet mensualisé
        txInteret = self.txInt()
        noPupsIf = self.nbrPupsIf
        noNewPups = self.nbrNewRed
        
        #  Possibilité de peut-être le faire sans loop (A VERIFIER)
        for i in range(1,self.shape[1]):
        
            pupBBenPP[:,i,:] = pupBBenPP[:,i-1,:] * txInteret[:,i,:]
            
            pbAcquAVPUP[:,i,:] = pbAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
# DIVISION PAR 0 A REGLER !!!!
            pbAcquAPPUP[:,i,:] = np.nan_to_num((pbAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBBenPP[:,i,:] * noNewPups[:,i,:]) / noPupsIf[:,i,:])
                  
    #Définition des variables récursives
        # PB acquise par police AVANT nouvelle réduction                                 
        self.pbAcquAVPUP=pbAcquAVPUP
        # PB acquise par police APRES nouvelle réduction 
        self.pbAcquAPPUP=pbAcquAPPUP
        # PB acquise
        self.pbAcquPP = pupBBenPP



# epargne acquise par police réduite APRES/AVANT nouvelles réductions
    def epargnAcqu(self):
        
        eppAcquAPPUP = self.zero()
        noPupsIf = self.nbrPupsIf
        noNewPups = self.nbrNewRed
        epAcquAVPUP = self.zero()
        txInteret = self.txInt()
        pupBenPP =self.epargAcqu()
        
        for i in range(1,self.shape[1]):
            
            epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
 # DIVISION PAR 0 A REGLER !!!!           
            eppAcquAPPUP[:,i,:] = np.nan_to_num((epAcquAVPUP[:,i,:] * (noPupsIf[:,i,:] - noNewPups[:,i,:]) + pupBenPP[:,i,:] * noNewPups[:,i,:]) / noPupsIf[:,i,:])

   #Définition des variables récursives
        #Epargne acquise par police AVANT nouvelle réduction                                 
        self.epAcquAVPUP=epAcquAVPUP
        #Epargne acquise par police APRES nouvelle réduction 
        self.eppAcquAPPUP=eppAcquAPPUP
        
        self.pupBenPP = pupBenPP


        
# benefice en cas de mort d'une police réduite
        
    def pupDeath(self):
        return np.nan_to_num(self.epAcquAVPUP + self.pbAcquAVPUP)
    



#  epargne et PB calculée au taux de PB
        
    # def eparPB(self):
        
    #     txIntAnn = self.p['POLINTERG'].to_numpy()[:,np.newaxis, np.newaxis] * self.one()/100
    #     initPB = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
    #     initEpargne = self.p['PMBPRVMAT'].to_numpy()[:,np.newaxis]
        
    #     eparPB = self.zero()
    #     eparPB[:,0,:] = initPB + initEpargne
        
    #     calendarMonth = self.calendarMonth()
        
    #     for i in range(1,self.shape[1]):
    #         # eparPB[:,i,:] = eparPB[:,i-1,:] * (1 + txIntAnn[:,i,:])/(1+ txIntAnn[:,i,:]**(((12 - (12-calendarMonth[:,i,:])%12 ))/12))
    #         eparPB[:,i,:] = eparPB[:,i-1,:] * (1 + txIntAnn[:,i,:])**(calendarMonth/12)

    #     return eparPB



# benefit en cas de mort (DEATH_OUTGO)
    def deathClaim(self):
        
        addSumAssuree = self.p['POLCAPAUT'].to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        
        deathBenefit = self.pbAcquPP + self.epargAcqu() + addSumAssuree
        
        deathClaim = deathBenefit * self.nbrDeath + self.pupDeath() * self.nbrPupDeath
        
        return np.nan_to_num(deathClaim)




    
    #Retourne la réserve mathémathique ajustée
    def adjustedReserve(self):

  # Age limite pour hospitalis
        self.agelimite=((self.age()-1)<=self.ageLimite)
           
        annualPrem =  (self.p['POLPRCPL9']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()   
        # riderC =  annualPrem * self.isPremPay() *self.dcAccident() * self.nbrPolIfSM
        self.agelimite = self.agelimite * self.one()
        #Calcul du risque en cours
        riderIncPP=annualPrem*self.agelimite*self.isPremPay()
        riderIncPP2=annualPrem*self.agelimite
        
# Ne prend pas en compte les risque en cours du modelpoint ??? à modifier
        # precPP=(self.p['PMBREC'] + self.p['PMBRECCPL']).to_numpy()[:,np.newaxis,np.newaxis] * self.one()
        precPP = self.zero()
        frek=self.frac()

        for i in range(1,self.shape[1]):
            precPP[:,i,:]=precPP[:,i-1,:]+riderIncPP[:,i,:] - ((frek[:,i,:]/12)*riderIncPP2[:,i,:])
            
        # CaFracPC=self.p['fraisFract'].to_numpy()[:,np.newaxis,np.newaxis]
        # CaPremPC=self.p['aquisitionLoading'].to_numpy()[:,np.newaxis,np.newaxis]
        
        # ppureEnc = (annualPrem * (1-CaPremPC) / CaFracPC)* self.isPremPay() *self.nbrPolIfSM
        
        # mathResBA=np.maximum(precPP,0)
        # mathResPP=mathResBA 
        # provMathIf=mathResPP*self.nbrPolIf
        # mathresIF=provMathIf
        
        # mathResIfcorr=self.zero()       
        # mathResIfcorr[:,1:,:]=mathresIF[:,:-1,:]  
        # mathResIfcorr = mathResIfcorr - riderC + ppureEnc

        # reserve=mathResIfcorr
        # reserve=np.maximum(reserve,0)
        
        return precPP
        
    
    
# Calcul des sorties dûes aux maturité des polices (MAT_OUTGO)
    def matOutgo(self):
        
        matBenPP = self.epargAcqu() + self.pbAcquPP
        noMats = self.nbrNewMat
        pupMatbPP =  self.epAcquAVPUP + self.pbAcquAPPUP
        noPupMat = self.nbrPupMat
        matOutgo = self.zero()
        
        for i in range(1,self.shape[1]):
            
            matOutgo[:,i,:] = matBenPP[:,i-1,:] * noMats[:,i,:] + pupMatbPP[:,i-1,:] * noPupMat[:,i,:]
           
 #Définition des variables récursives
        self.matBenPP = matBenPP
        self.noMats = noMats
        self.pupMatbPP = pupMatbPP
        self.noPupMat = noPupMat
        
        # return matBenIF + matBenPPUPif
        return matOutgo
    
    
    def mathresBA(self):
        # return self.epargAcqu() + self.pbAcquPP 
        return self.epargAcqu() + self.pbAcquPP + self.adjustedReserve()      


#  benefit en cas d'annulation (SURR_OUTGO)    
    def surrOutgo(self):
        
    # Surrender outgo pour les polices non réduites:
        surrIf = self.mathresBA() * self.nbrSurrender
        
    # Surrender Outgo pour les polices réduites:
        surrRed = (self.pbAcquAPPUP + self.eppAcquAPPUP) * self.nbrPupSurrender
         
        return surrIf + surrRed
    
  
 # ici on détermine le capital pour Protection d'avenir en fonction de l'âge
    def capPA(self):
        
        capPA = self.zero()
        capPA[self.age() <= 55]= 25000
        capPA[(self.age() > 55)]= 5000
        capPA[self.age() > 65]= 0
        capPA[self.p['POLPRCPL9'] == 0]=0
        return capPA
    
    
    
    
# prime complémentaire encourue
    
    def riderCostPP(self):
        
    # Age limite pour mod28
        self.agelimite=((self.age()-1)<=self.ageLimite)
           
        annualPrem =  (self.p['POLPRCPL9']).to_numpy()[:,np.newaxis,np.newaxis]
        annualPrem = annualPrem / self.frac()   
        riderC =  annualPrem * self.isPremPay() * self.dcAccident() 

        return riderC
    

# benefice en cas de sinistre complémentaire (RIDERC_OUTGO)
    def riderCOutgo(self):
        
        riderCoutgo = self.riderCostPP() * self.nbrPolIfSM + self.nbrDeath * self.capPA()
        
        return riderCoutgo

        

# Total prestations
    def totalClaim(self):
        
        return self.surrOutgo() + self.deathClaim() + self.riderCOutgo() + self.matOutgo()
    
    
    
    
    
##############################################################################################################################
###################################  CALCUL DES EXPENSES  #############################################################
##############################################################################################################################
    
    
    #Retourne le coût par police pour les polices avec réduction possible
    def unitExpenseRed(self):
        
        inflation=np.roll(self.inflation(),[1],axis=1)
        inflation[:,0,:]=0
        
        coutParPolice=self.fraisGestion()

        cost=coutParPolice*inflation*(self.nbrPolIfSM + self.nbrPupIfSM)
        
        return cost

    
    
    # Calcul des provisions mathématiques en cours
    def provMathIf(self):
        
        provMathIf = self.mathresBA() * self.nbrPolIf + (self.eppAcquAPPUP + self.pbAcquAPPUP) * self.nbrPupsIf
    
        return provMathIf
    
    
    
    
    # calcul des provisions techniques en cours, inforce
    def provTechIf(self):
        
        provTechPP = self.mathresBA() - self.adjustedReserve()
        
        pupMathRes = self.eppAcquAPPUP + self.pbAcquAPPUP
        
        provTechIf = provTechPP * self.nbrPolIf + self.nbrPupsIf * pupMathRes
    
        return provTechIf
    
    
    
    #  calcul des provisions techniques ajustée (PROV_TECH_AJ)
    def provTechAj(self):
        
        provTechAj = self.zero()
        provTechIf = self.provTechIf()
        primeInvest = self.prEncInvPP() * self.nbrPolIfSM
        riderCoutgo = self.riderCOutgo()
        
        for i in range(1,self.shape[1]):
        
            provTechAj[:,i,:] = provTechIf[:,i-1,:] + primeInvest[:,i,:] - riderCoutgo[:,i,:]
        
        return provTechAj
    
    
    # calcul des intêret techniques crédités (INT_CRED_T)
    def intCred(self):
        
        return (self.txInt()-1) * self.provTechAj()
    
    
    #  calcul des primes investies (PRIME_INVEST)
    def primeInvest(self):
        return self.prEncInvPP() * self.nbrPolIfSM
    
    
    
    
    
#  Calcul des réserve mathématiques adjustées
    def reserveForExp(self):
        
        provMathIf = self.provMathIf()
        riderCoutgo = self.riderCOutgo()
        adjMathRes2 = self.zero()
        rfinAnn = self.zero()
        resFinMois = self.zero()
        totIntCred = self.zero()
        oTaxblInc = self.zero()
        txInt = self.txInt()
        provTechAj = self.provTechAj()
        rfinMonth = self.rfinMonth()
        totIntCred =  self.intCred()
        rate = self.rate()
        premInvest = self.primeInvest()
        premInc = self.totalPremium()
        
        unitExp = self.unitExpenseRed()
        txReserve = self.fraisGestionPlacement()
        totExp = self.zero()
        provMathAj = self.zero()
        resReldMat = self.zero()
        mathresPP = self.mathresBA()
        noMat = self.nbrNewMat
        pupMathRes = self.eppAcquAPPUP + self.pbAcquAPPUP
        nbrPupMat = self.nbrPupMat
        noPolif = self.nbrPolIf
        noPupsIf = self.nbrPupsIf
        
        for i in range(1,self.shape[1]):
            
 
            adjMathRes2[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInvest[:,i,:] - riderCoutgo[:,i,:]
        
            totExp[:,i,:] = unitExp[:,i,:] + adjMathRes2[:,i,:] * txReserve[:,i,:]  
            
            resReldMat[:,i,:] = np.nan_to_num((mathresPP[:,i-1,:] * noMat[:,i,:] + pupMathRes[:,i-1,:] * nbrPupMat[:,i,:] + rfinAnn[:,i-1,:]) / (noPolif[:,i-1,:] + noPupsIf[:,i-1,:])*(noMat[:,i,:] + nbrPupMat[:,i,:]))
            
            provMathAj[:,i,:] = provMathIf[:,i-1,:] + rfinAnn[:,i-1,:] + premInc[:,i,:] - riderCoutgo[:,i,:] - totExp[:,i,:] - resReldMat[:,i,:]
        
            oTaxblInc[:,i,:] = provMathAj[:,i,:] * rate[:,i,:]
            
            resFinMois[:,i,:] = oTaxblInc[:,i,:] - totIntCred[:,i,:]
            
            rfinAnn[:,i,:] = (rfinAnn[:,i-1,:] + resFinMois[:,i,:]) * rfinMonth[:,i,:]
            
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

        self.resReldMat = resReldMat
        
        return self
    
    
    def totalExpense(self):
        return self.adjMathRes2 * self.fraisGestionPlacement() + self.unitExpenseRed()
    
    
    
    
    
    def test(self):
        
        return self.pbAcquPP + self.epargAcqu() + self.addSumAssuree 
    
##############################################################################################################################
###################################DEBUT DES TESTS DE LA CLASSE ET FONCTIONALITES#############################################
##############################################################################################################################
    def tester(self):
        return self

pol = EPP28()
# pol.ids([605701, 532301])
# matougto = pol.matOutgo()
# benpp = pol.matBenPP
# nomat = pol.noMats
# pupmat = pol.pupMatbPP
# nopupmat = pol.noPupMat
# surrOutgo = pol.surrOutgo()
# eppAcquAPPUP = pol.eppAcquAPPUP
# pbAcquAPPUP = pol.pbAcquAPPUP
# riderincpp = pol.riderCostPP()
# totclaim = pol.totalClaim()
# protectionavenir = pol.capPA()
# provtechIf = pol.provTechIf()
adjMathRes2 = pol.adjMathRes2
provMathAj = pol.provMathAj
oTaxblInc=pol.oTaxblInc
totalExpense = pol.totalExpense()
resfin = pol.rfinAnn
resfinmois = pol.resFinMois
resReldMat = pol.resReldMat
matoutgo = pol.matOutgo()
provmathif = pol.provMathIf()
provtechAj = pol.provTechAj()
riecostoutgo = pol.riderCOutgo()
# provmathAj = pol.provMathAj()
# testt = pol.test()
# mathresBA = pol.mathresBA()
nopupif = pol.nbrPupsIf
nomat = pol.noMats
# nonvewred = pol.nbrNewRed
# epAcquAVPUP = pol.epAcquAVPUP
# eppAcquAPPUP33 = pol.eppAcquAPPUP
# pupEben = pol.pbAcqu()
deathbenef = pol.deathClaim()
# pupdthbPP = pol.pupDeath()
# pbAcquAVPUP = pol.pbAcquAVPUP
# pbacquAPPUP = pol.pbAcquAPPUP
# deathpup=pol.nbrPupDeath
# epargneacquise = pol.epargAcqu()
# pbacquPP= pol.pbAcquPP
# eparPB = pol.eparPB()
# check = pol.ppurePP()
# check2 = pol.prEncInvPP()
# epp = pol.epargAcqu()
# pbb = pol.pbAcqu()
# pol = HO()
#pol=AX()
#pol=AX(run=[4,5])
# chck = pol.isVal()
adjustRES = pol.adjustedReserve()
#pol.mod([70])
# pol.modHead([3],1)
# aa = pol.p
# cc= pol.accidentalDeathClaim()
# oo = pol.nbrNewPups
a=pol.nbrPolIf
b=pol.nbrPolIfSM
#c=pol.nbrMaturities
d=pol.nbrDeath
e=pol.nbrSurrender
#f=pol.premiumCompl()
#g=pol.purePremium()
# h=pol.deathClaim()
#i=pol.fraisVisiteClaim()
#j=pol.timeBeforeNextPay()
#k=pol.risqueEnCour()
# l=pol.adjustedReserve()
# m=pol.reserveExpense()
n=pol.unitExpenseRed()
o=pol.totalPremium()
# q=pol.totalClaim()
r=pol.totalCommissions()
# s=pol.totalExpense()
# t=pol.BEL()
#u=pol.polTermM
# t = pol.claimCompl()
# tt = pol.adjustedReserve()
bel=np.sum(pol.BEL(), axis=0)
#pgg=pol.PGG()
# ll = pol.l_val()
nn = pol.nbrNewRed
pupbenPPP = pol.pupBenPP
print("Class X--- %s sec" %'%.2f'%  (time.time() - start_time))

 # pol.p=pol.modHead(pol.modHeads)

iii = pol.eppAcquAPPUP


##############################################################################################################################
#TESTER DES CAS
##############################################################################################################################

def testerCas(self):
    return self
# iii = pol.totalPrem()
monCas=matoutgo
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(r'check.csv',header=False)

ss = pol.p
ss.to_excel("check portefeuille.xlsx", header = True )
#Visualiser une dimension d'un numpy qui n'apparait pas
# test = pol.reduction()
# data=pupEben
# a=pd.DataFrame(data[:,:,0])
