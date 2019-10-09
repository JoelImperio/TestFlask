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
    primecompl = 60
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        
#Calcul des inforce
  
    def nbinforce(self):
           
        qxmens = self.qxmensuel()
        myPayement = self.mypayement()  
        
        lapseann = np.asarray(hyp.lapse(self), dtype=np.float64)
        lapsemens = np.asarray(1-(1-hyp.lapse(self))**(1/self.fractionnement()), dtype=np.float64)

        nbSurr = self.zeros()
        nbDeath = self.zeros()
        no_pol_if = self.zeros()
        no_pol_if[:,0,:] = 1
        
        for i in range(1,np.size(self,1)-1):
# JO Prophet affiche ce calcul mais l'effectue sans prendre en compte lapsemens A VERIFIER
#            nbDeath[:,i,:] = no_pol_if[:,i-1,:] * qxmens[:,i,:] * (1- (lapsemens[:,i,:] * myPayement[:,i+1,:])/2)
            
            nbDeath[:,i,:] = no_pol_if[:,i-1,:] * qxmens[:,i,:]
            nbSurr[:,i,:] = no_pol_if[:,i-1,:]  * lapsemens[:,i,:] * (1- qxmens[:,i,:]/2) * myPayement[:,i+1,:] 
            no_pol_if[:,i,:] = no_pol_if[:,i-1,:] - nbSurr[:,i,:] - nbDeath[:,i,:]

        no_pol_if[no_pol_if <= 0] = 0
        nbSurr[nbSurr < 0] = 0
    
# JO ajout de la condition sur l'âge
#        condlist = [self.age() < 65, self.age() >= 65]
#        choicelist = [no_pol_if , no_pol_if ==0]
#        
#        no_pol_if=np.select(condlist, choicelist)
        
        no_pol_if = no_pol_if * FU.isactive(self)
        
# JO force la dernière valeur à 0, sinon = 1 POURQUOI ? A CHANGER !!!
        no_pol_if[:,np.size(self,1)-1,:] = 0
             
        return no_pol_if, nbDeath, nbSurr
       
        
# JO créer un vecteur avec des 1 et 0 si la police est toujours active selon l'age
    def isactive(self):
        
        isactive = self.un
        condlist = [np.minimum(self.age(1), self.age(2)) < 65, np.minimum(self.age(1), self.age(2)) >= 65]
        choicelist = [isactive , isactive ==0]
        isactive=np.select(condlist, choicelist)
        
        return isactive



    def inforce(self):
        
        return FU.nbinforce(self)[0]


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
        
        nombredeath = FU.nbinforce(self)[1]
        
        condlist = [self.age() < 65, self.age() >= 65]
        choicelist = [nombredeath , nombredeath ==0]
        nombredeath=np.select(condlist, choicelist)
        
        return nombredeath



    def deathClaim(self):
        return FU.nbdeath(self) * self.p['PMBCAPIT'].to_numpy()[:,np.newaxis,np.newaxis]
    


    def surrClaim(self):
    
        txsin = hyp.fraisVisite()
        primcpl = ((self.zeros() + 60)/self.fractionnement()) * txsin * FU.mypayement(self) * FU.inforceSM(self)
        primcpl = primcpl * FU.isactive(self)
        
        return primcpl
        
    
    def totClaim(self):
        return FU.surrClaim(self) + FU.deathClaim(self)
    
    
    def mathexp(self):
        pass
        
    
    def renexp(self):
# JO créer array inflation        
        inflation = 1.0125**(np.arange(np.size(self,1))[np.newaxis,:,np.newaxis]/12)

        return (hyp.fraisGestion(self)/12)* inflation * FU.inforceSM(self)
        

#sp=FU()       
#b=sp.un
#c=sp.vide
#kk=policies.un
#d=sp.p
#bbb = FU.inforce(policies)
#z = FU.inforce(policies)