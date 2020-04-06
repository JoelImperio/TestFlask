from Portefeuille import Portfolio
from Parametres import allRuns
#from Produits import FU
#from RunPGG import RUNPGG
import numpy as np
import pandas as pd
import time
import os, os.path
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
    
    def __init__(self,run=allRuns,\
                 PortfolioNew=True, SinistralityNew=True,LapseNew=True,CostNew=True,RateNew=True ):
        super().__init__(runs=run,\
             myPortfolioNew=PortfolioNew, mySinistralityNew=SinistralityNew,myLapseNew=LapseNew,myCostNew=CostNew,myRateNew=RateNew)
        self.p=self.mod(self.mods)
        

#Permet de relancer l'update() en intégrant des methodes de la sous-classe
    def update(self,subPortfolio):
        super().update(subPortfolio)
        self.loopSaving()

# #Cette Loop renvoie l'ensemble des variables récusrives pour les produits mixtes
#     def loopEndowment(self):

# #Variables des actifs            
#         nbrPolIf=self.one()
#         nbrPolIfSM=self.zero()
#         nbrDeath=self.zero()
#         nbrSurrender=self.zero()
#         nbrMaturities=self.zero()
#         nbrNewRed = self.zero()
#         matRate=self.zero()
             
        
# #Variables biométriques et génériques
#         lapseTiming=0.5
#         polTermM=self.polTermM()       
#         lapseD=lapseTiming * self.lapse()
#         lapse = self.lapse()        
#         reduction = self.reduction()       
#         qxy=self.qxyExpMens()
#         qxyD =lapseTiming * self.qxyExpMens()

        
#         #Définition du vecteur des maturités (bool)        
#         matRate[polTermM+1 ==self.durationIf()]=1 
            
#         for i in range(1,self.shape[1]):

# #Définition des variables des actifs            
#             nbrMaturities[:,i,:]=nbrPolIf[:,i-1,:]*matRate[:,i,:]
            
#             nbrPolIfSM[:,i,:]=nbrPolIf[:,i-1,:] - nbrMaturities[:,i,:]
            
#             nbrDeath[:,i,:]=nbrPolIfSM[:,i,:]*qxy[:,i,:]*(1-(lapseD[:,i,:]))
            
#             nbrSurrender[:,i,:]=nbrPolIfSM[:,i,:]*lapse[:,i,:]*(1-(qxyD[:,i,:]))
            
#             # nbrNewRed[:,i,:] = (nbrPolIf[:,i-1,:] - nbrDeath[:,i,:] - nbrSurrender[:,i,:] - nbrMaturities[:,i,:]) * reduction[:,i,:]
            
#             # nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:]- nbrNewRed[:,i,:] - nbrMaturities[:,i,:]

          
#             nbrPolIf[:,i,:]=nbrPolIf[:,i-1,:]-nbrDeath[:,i,:]-nbrSurrender[:,i,:] - nbrMaturities[:,i,:]


# #Sauvegarde des variables des actifs
       
#         #Nombre de polices actives                                 
#         self.nbrPolIf=nbrPolIf
#         #Nombre de police actives en déduisant les échéances du mois
#         self.nbrPolIfSM=nbrPolIfSM
#         #Nombre de décès
#         self.nbrDeath=nbrDeath
#         #Nombre d'annulation de contrat
#         self.nbrSurrender=nbrSurrender
#         #Nombre de nouvelle réduction
#         self.nbrNewRed = nbrNewRed
#         # Nombre de nouvelle maturités
#         self.nbrNewMat = nbrMaturities
             
        
#         return


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
        # allocMonths = self.allocMonths()
        
   
        # Taux annualisé
        txIntPC = self.txInt()**(12) - 1
        # txPbPC = self.txPbPC()/100
        
        # taux annualisé
        txIntPC = self.txInt()**(12) - 1
        # epgTxPB_PP = self.epgTxPB_PP()
        
        # txTot = 1 + (txPbPC + txIntPC)
        
        pbIncorPP = self.zero()
        pbAcquPP = self.zero()
        pbAcquPP[:,0,:] = self.p['PMBPBEN'].to_numpy()[:,np.newaxis]
        pbCalcPP = self.zero()
        # isActive = self.isActive()
        
        
        pbCalcPPdths = self.zero()
        pbCalcPUPdths = self.zero()
        
     
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
        
        
        
        qxyD =lapseTiming * qxy
        txInteret = self.txInt()
        # prEncInv = self.premiumInvested()

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

#Définition des variables d'épargne pour actives et réduites
#             epargnAcquPP[:,i,:]= (epargnAcquPP[:,i-1,:] + prEncInv[:,i,:]) * txInteret[:,i,:]

#             epAcquAVPUP[:,i,:] = eppAcquAPPUP[:,i-1,:] * txInteret[:,i,:]
            
#             epTemp = epAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + epargnAcquPP[:,i,:] * nbrNewRed[:,i,:]
            
#             eppAcquAPPUP[:,i,:] = np.divide(epTemp,nbrPupsIf[:,i,:],out=np.zeros_like(epTemp), where=nbrPupsIf[:,i,:]!=0)

            
# #Définition des variables de PB pour actives et réduites      
#             pbIncorPP[:,i,:] = np.nan_to_num(pbCalcPP[:,i-1,:] *  isActive[:,i-1,:])
            
#             pbIncorPUP[:,i,:] = np.nan_to_num(pbCalcPUP[:,i-1,:]  * isActive[:,i-1,:]) 

#             pbSortDTHS[:,i,:] = np.nan_to_num(pbCalcPPdths[:,i,:] * isActive[:,i,:]) 
            
#             pbPupDTHS[:,i,:] = np.nan_to_num(pbCalcPUPdths[:,i,:] * isActive[:,i,:]) 
         
#             pbAcquAVPUP[:,i,:] = (pbAcquAPPUP[:,i-1,:] + pbIncorPUP[:,i,:]) * txInteret[:,i,:]

#             pbAcquPP[:,i,:] = (pbAcquPP[:,i-1,:] + pbIncorPP[:,i,:]) * txInteret[:,i,:] * isActive[:,i,:]            

#             pbTemp=pbAcquAVPUP[:,i,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) + pbAcquPP[:,i,:] * nbrNewRed[:,i,:]            
            
#             pbAcquAPPUP[:,i,:] = np.divide(pbTemp,nbrPupsIf[:,i,:],out=np.zeros_like(pbTemp), where=nbrPupsIf[:,i,:]!=0)       
  
#             epgTxTEMP = epgTxPbPUP[:,i-1,:] * (nbrPupsIf[:,i,:] - nbrNewRed[:,i,:]) * (txTot[:,i,:]**(1/12)) + (epgTxPB_PP[:,i,:] *  nbrNewRed[:,i,:])
            
#             epgTxPbPUP[:,i,:] =  np.divide(epgTxTEMP, nbrPupsIf[:,i,:], out=np.zeros_like(epgTxTEMP), where=nbrPupsIf[:,i,:]!=0)
               
#             pbCalcPP[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0)  * allocMonths[:,i,:]
            
#             pbCalcPUP[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * allocMonths[:,i,:]
            
#             pbCalcPPdths[:,i,:] = np.maximum((epgTxPB_PP[:,i,:] - epargnAcquPP[:,i,:] - pbAcquPP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
#             pbCalcPUPdths[:,i,:] = np.maximum((epgTxPbPUP[:,i,:] - eppAcquAPPUP[:,i,:] - pbAcquAPPUP[:,i,:]),0) * (1 - allocMonths[:,i,:])
            
#             pbSortMatsPP[:,i,:] = pbCalcPP[:,i,:] * isActive[:,i,:]
            
#             pbSortMatsPUP[:,i,:] = pbCalcPUP[:,i,:] * isActive[:,i,:]

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
#         self.pbCalcPP = pbCalcPP
#         # PB acquise des polices actives
#         self.pbAcquPP = pbAcquPP
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
        
        return




# Prime complémentaire qui va dépendre de la modalité et du tarif
    def annRider(self):
        
        # Prime complémentaire pour les mixtes
        primeCompl = (self.p['POLPRCPL1'] + self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL5']\
                      + self.p['POLPRCPL6'] + self.p['POLPRCPL9'])[:,np.newaxis,np.newaxis] * self.one()
            
        # Prime complémentaire pour les taux d'interet inférieur à 2.5 et age dépassant 65
        primeCompl2 = (self.p['POLPRCPL3'] + self.p['POLPRCPL4'] + self.p['POLPRCPL9'])[:,np.newaxis,np.newaxis] * self.one()
        
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
        prem=(premInc*self.indexation() + premCompl) *self.nbrPolIfSM*self.isPremPay()
        
        return prem


#Retourne les claims de la garantie principale (DEATH_OUTGO)
    def claimPrincipal(self):
        return self.zero()

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
# pol.ids([393305])
pol.modHead([2],1)

    ### Mod 2_2 F2XT_1
# pol.ids([2501])
# pol.modHead([2],2)

    ### Mod 10 F1XT14
# pol.ids([1602604])
# pol.mod([10])

    ### Mod 6 F1XT11
# pol.ids([799003])
# pol.mod([6,7])
age = pol.age()




# a = pol.p
b=pol.nbrPolIf
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

monCas=p
zz=np.sum(monCas, axis=0)
zzz=np.sum(zz[:,0])
z=pd.DataFrame(monCas[:,:,0])
z=z.sum()
z.to_csv(path+'/zJO/check.csv',header=False)


# aaa=aa[['PMBPOL', 'PMBFRACT','POLSIT','PMBMOD','PMBTXINT']]



pol.p.to_excel(path+'/zJO/check portefeuille.xlsx', header = True )
# aa.to_excel("check portefeuille.xlsx", header = True )


#Visualiser une dimension d'un numpy qui n'apparait pas
#data=pol.lapse()
#a=pd.DataFrame(data[:,:,4])

a = pol.p

