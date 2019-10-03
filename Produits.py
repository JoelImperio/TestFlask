from Portefeuille import Portfolio
from Parametres import Hypo

import numpy as np
import pandas as pd

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM95, EKF95


tariff = MortalityTable(nt=EKM95)



import pandas as pd
import numpy as np
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



#Calcul des inforce

    def inforce(self):
        
#       ligne de code qui évite un code d'erreur
        qxmens = np.array(-1, dtype=np.complex)
        qxmens = 1-(1-self.qx(table=GKF95, exp=27.06,ass=1))**(1/12)
        lapsemens = 1-(1-hyp.lapse(self))**(1/12)

        
        nbSurr = self.zeros()
        nbDeath = self.zeros()
        no_pol_if = self.zeros()
        no_pol_if[:,0,:] = 1


        for i in range(1,np.size(self,1)):
            
            
            
            nbDeath[:,i,:] = no_pol_if[:,i-1,:] * qxmens[:,i,:]
#            nbSurr[:,i,:] = (no_pol_if[:,i-1,:] - nbDeath[:,i,:]) * lapsemens[:,i,:]
            
            nbSurr[:,i,:] = no_pol_if[:,i-1,:] * lapsemens[:,i,:] * (1- (qxmens[:,i,:]/2))
            no_pol_if[:,i,:] = no_pol_if[:,i-1,:] - nbSurr[:,i,:] - nbDeath[:,i,:]
            
#            no_pol_iffadd=np.add(no_pol_if[:,(i-1),:]+0.01, no_pol_if[:,i:,:], no_pol_if[:,i:,:])


        no_pol_if[no_pol_if < 0] = 0
        nbSurr[nbSurr < 0] = 0

        return no_pol_if



    def premium(self):
        
        primes = self.zeros()
        fract = self.fractionnement()
        payement = self.zeros()
        
        condlist = [fract ==1,fract ==2,fract ==4,fract ==6,fract ==12]
                   
        
        choicelist = [payement[:,0,:],commissionsRates[:,1,:],commissionsRates[:,2,:], \
                      commissionsRates[:,3,:],commissionsRates[:,4,:]]
        
        myCommissions=np.select(condlist, choicelist)
        
        
        return fract


#sp=FU()       
#b=sp.un
#c=sp.vide
#kk=policies.un

#d=sp.p
#bbb = FU.inforce(policies)
#z = FU.inforce(policies)

