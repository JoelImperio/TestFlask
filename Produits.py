from Portefeuille import Portfolio
from Parametres import Hypo

import numpy as np
import pandas as pd

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM95, EKF95

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
        
#Calcul des inforce
  
    def nbinforce(self):
           
# JO ligne de code qui évite un code d'erreur   
        qxmens = np.array(-1, dtype=np.complex)
    
# JO Calcul qx mensuel du 1er assuré
        qxmens1 = 1-(1-self.qx(exp=41.73,ass=1))**(1/12)
        qxmens1[:,0,:] = 0
        
# JO Calcul qx mensuel du 2ème assuré
        qxmens2 = 1-(1-self.qx(exp=41.73,ass=2))**(1/12)
        qxmens2[:,0,:] = 0
        
# JO calcul du qx total si il y a 2 têtes et prend le qx du 1er assuré s'il y a une tête
        condlist = [self.nbassure() ==1, self.nbassure() ==2]
        choicelist = [qxmens1 , qxmens1 + qxmens2 - qxmens1*qxmens2 ]
        qxmens=np.select(condlist, choicelist)
        
        
        lapseann = np.asarray(hyp.lapse(self), dtype=np.float64)
        lapsemens = np.asarray(1-(1-hyp.lapse(self))**(1/self.fractionnement()), dtype=np.float64)

        nbSurr = self.zeros()
        nbDeath = self.zeros()
        no_pol_if = self.zeros()
        no_pol_if[:,0,:] = 1
        myPayement = self.mypayement()    

        for i in range(1,np.size(self,1)-1):
            
            nbDeath[:,i,:] = no_pol_if[:,i-1,:] * qxmens[:,i,:] * (1- (lapsemens[:,i,:] * myPayement[:,i+1,:])/2)
            nbSurr[:,i,:] = no_pol_if[:,i-1,:]  * lapsemens[:,i,:] * (1- qxmens[:,i,:]/2) * myPayement[:,i+1,:] 
            no_pol_if[:,i,:] = no_pol_if[:,i-1,:] - nbSurr[:,i,:] - nbDeath[:,i,:]

        no_pol_if[no_pol_if <= 0] = 0
        nbSurr[nbSurr < 0] = 0
    
# JO ajout de la condition sur l'âge
        condlist = [self.age() <= 65, self.age() > 65]
        choicelist = [no_pol_if , no_pol_if ==0 ]
        
        no_pol_if=np.select(condlist, choicelist)
# JO force la dernière valeur à 0, sinon = 1 POURQUOI ? A CHANGER !!!
        no_pol_if[:,np.size(self,1)-1,:] = 0
             
        return no_pol_if, nbDeath, nbSurr
        



# JO création d'un vecteur d'inforce décallé d'un mois : no_pol_ifsm  
    def inforceSM(self):      

        inforce = FU.inforce(self)
        no_pol_ifsm = self.zeros()
        
        no_pol_ifsm = np.roll(inforce, [1], axis=(1))
        no_pol_ifsm[:,0,:] = 0
       
        return no_pol_ifsm
    
    
    
# JO primes inforce
    def premium(self):
        
        premInc = int(self.p['POLPRTOT'])
        premium = FU.inforceSM(self) * premInc * self.mypayement()
        
        return premium



    def nbdeath(self):
        return FU.nbinforce(self)[1]



    def deathClaim(self):
        return FU.nbdeath(self) * 15000
    




#sp=FU()       
#b=sp.un
#c=sp.vide
#kk=policies.un
#d=sp.p
#bbb = FU.inforce(policies)
#z = FU.inforce(policies)