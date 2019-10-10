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
        
        premInc = self.p['POLPRTOT'][:,np.newaxis,np.newaxis] * policies.un
        premium = FU.inforceSM(self) * premInc * self.mypayement()/self.fractionnement()
        
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
        
        inflation = self.inflation()
        renexp_pp = (hyp.fraisGestion(self)/12)* inflation 
        
        renexp  = np.roll(renexp_pp, [1], axis=(1)) * FU.inforceSM(self)
        renexp = renexp * FU.isactive(self)
        
        return renexp
        
    
    def risqueEncour(self):
# JO temps écoulé en année depuis le dernie payement timelastp
        timelastp = self.fractionnement()*(self.durationIf()+11)/12 - np.floor(self.fractionnement() * (self.durationIf()+11)/12 )
        timelastp[:,0,:] = 0
        
        timelastp  = np.roll(timelastp, [-1], axis=(1))
        
        premInc = self.p['POLPRTOT'][:,np.newaxis,np.newaxis] * self.un
# JO premium charge de 20% CHIFFRE EN DUR A MODIFIER !!!
        rencours = (premInc * (1-timelastp)/self.fractionnement()) * (1-0.2)
        
        condlist = [timelastp == 0, timelastp != 0]
        choicelist = [rencours == 0 , rencours]
        rencours=np.select(condlist, choicelist)
        
        
        return rencours
    
# JO reserve mathématique adjusté pour calculé les dépenses lié au placement (mod89 = uniquement les risques en cours)
    def adjmathres(self):
# JO risque en cours décalé
        risqudec = np.roll(FU.risqueEncour(self), [1], axis=(1))
        
        primcpl = ((self.zeros() + 60)/self.fractionnement()) * FU.mypayement(self) * FU.inforceSM(self)
        primcpl = primcpl * FU.isactive(self)
        mathres = (FU.premium(self) - primcpl) * (1-0.2)- FU.surrClaim(self) + risqudec * FU.inforceSM(self)
        mathres = FU.isactive(self) * mathres
        
        return mathres
    
    def placementexp(self):
        
        placementexp = FU.adjmathres(self) * hyp.fraisGestionPlacement()/1200
        
        return placementexp
    
    
    def totexp(self):
        
        return FU.placementexp(self) + FU.renexp(self) 
    
    
    def commTot(self):
        
        commissions = hyp.commissions(self) * FU.premium(self)
        
        return commissions.astype(float)
#* FU.inforceSM(self)
#sp=FU()       
#b=sp.un
#c=sp.vide
#kk=policies.un
#d=sp.p
#bbb = FU.inforce(policies)
#z = FU.inforce(policies)