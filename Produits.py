from Portefeuille import Portfolio
from Parametres import Hypo

import numpy as np
import pandas as pd

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM95, EKF95


tariff = MortalityTable(nt=EKM95)



import pandas as pd
import numpy as np
from Portefeuille import dateCalcul
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i

import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

#Ceci est une class d'exemple pour reprendre merci de ne pas toucher
class FU(Portfolio):
    mods=[8,9]
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)



#Ajout vecteur de 1 ou 0 si il y a paiement de prime ou non
    def mypayement(self):
        
        payement = self.zeros()
        
        check1 = (fract * (self.durationIf() + 11) /12)
        check2 = np.floor((fract * (self.durationIf() + 11) /12))
        
        condlist = [check1 - check2 == 0, check1 - check2 != 0]
        choicelist = [payement[:,1,:]==0, payement[:,1,:] ==1 ]
        
        myPayement=np.select(condlist, choicelist)

        return myPayement


#Calcul des inforce

    def inforce(self):
        
        primes = self.zeros()
        fract = int(self.fractionnement())
        

        
#       ligne de code qui évite un code d'erreur
        qxmens = np.array(-1, dtype=np.complex)
        qxmens = 1-(1-self.qx(exp=41.73,ass=1))**(1/12)
        qxmens[:,0,:] = 0

        lapseann = np.asarray(hyp.lapse(policies), dtype=np.float64)
        lapsemens = np.asarray(1-(1-hyp.lapse(policies))**(1/fract), dtype=np.float64)

        nbSurr = self.zeros()
        nbDeath = self.zeros()
        no_pol_if = self.zeros()
        no_pol_if[:,0,:] = 1
#        test1 = self.zeros()

        for i in range(1,np.size(self,1)-1):
            
#            test1[:,i,:] = (lapsemens[:,i,:] * myPayement[:,i+1,:])
            
            nbDeath[:,i,:] = no_pol_if[:,i-1,:] * qxmens[:,i,:] * (1- (lapsemens[:,i,:] * FU.mypayement(self)[:,i+1,:])/2)
            nbSurr[:,i,:] = no_pol_if[:,i-1,:]  * lapsemens[:,i,:] * (1- qxmens[:,i,:]/2) * FU.mypayement(self)[:,i+1,:] 
            no_pol_if[:,i,:] = no_pol_if[:,i-1,:] - nbSurr[:,i,:] - nbDeath[:,i,:]

        no_pol_if[no_pol_if < 0] = 0
        nbSurr[nbSurr < 0] = 0
    

        
    
        return no_pol_if

    def inforceSM(self):
        
# JO création d'un vecteur décallé d'un mois no_pol_ifsm  
        inforce = FU.inforce(self)
        no_pol_ifsm = self.zeros()
        
        no_pol_ifsm = np.roll(inforce, [1], axis=(1))
        no_pol_ifsm[:,0,:] = 0
       
        return no_pol_ifsm
    

    def premium(self):
        
        premInc = int(self.p['POLPRTOT'])
        premium = FU.inforceSM(self) * premInc * FU.mypayement(self)
        
        
        return premium


#sp=FU()       
#b=sp.un
#c=sp.vide
#kk=policies.un

#d=sp.p
#bbb = FU.inforce(policies)
#z = FU.inforce(policies)

