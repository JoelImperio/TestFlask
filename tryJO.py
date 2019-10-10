import numpy as np
import pandas as pd
import time

import os, os.path
from Portefeuille import Portfolio
from Parametres import Hypo




# Python program for
# iterating array values
# using external loop
 

#
#primes = policies.zeros()
#fract = int(policies.fractionnement())
#payement = policies.zeros()
#        
##Ajout vecteur de 1 ou 0 si il y a paiement de prime ou non
#check1 = (fract * (policies.durationIf() + 11) /12)
#check2 = np.floor((fract * (policies.durationIf() + 11) /12))
#        
#condlist = [check1 - check2 == 0, check1 - check2 != 0]
#choicelist = [payement[:,1,:]==0, payement[:,1,:] ==1 ]
#myPayement=np.select(condlist, choicelist)
#        
#    
#
#
#
##       ligne de code qui évite un code d'erreur
#qxmens = np.array(-1, dtype=np.complex)
#qxmens = 1-(1-policies.qx(exp=41.73,ass=1))**(1/12)
#qxmens[:,0,:] = 0
#        
#
#
#lapseann = np.asarray(hyp.lapse(policies), dtype=np.float32)
#lapsemens = np.asarray(1-(1-hyp.lapse(policies))**(1/fract), dtype=np.float32)
#
# 
#
#
#        
#nbSurr = policies.zeros()
#nbDeath = policies.zeros()
#no_pol_if = policies.zeros()
#no_pol_if[:,0,:] = 1
#
#test1 = policies.zeros()
##        dernier jour de projection pas de paiement (A CHANGER)
#        
##        myPayement[:,np.size(self,1) +1,:] = 0
#
#for i in range(1,np.size(policies,1)-1):
#            
#    test1[:,i,:] = (lapsemens[:,i,:] * myPayement[:,i+1,:])
#    nbDeath[:,i,:] = no_pol_if[:,i-1,:] * qxmens[:,i,:] * (1- (lapsemens[:,i,:] * myPayement[:,i+1,:])/2)
##            nbSurr[:,i,:] = (no_pol_if[:,i-1,:] - nbDeath[:,i,:]) * lapsemens[:,i,:]
#            
#    nbSurr[:,i,:] = no_pol_if[:,i-1,:]  * lapsemens[:,i,:] * (1- qxmens[:,i,:]/2) * myPayement[:,i+1,:] 
#    no_pol_if[:,i,:] = no_pol_if[:,i-1,:] - nbSurr[:,i,:] - nbDeath[:,i,:]
#            










#
## JO temps écoulé en année depuis le dernie payement timelastp
#timelastp = policies.fractionnement()*(policies.durationIf()+11)/12 - np.floor(policies.fractionnement() * (policies.durationIf()+11)/12 )
#timelastp[:,0,:] = 0
#        
#timelastp  = np.roll(timelastp, [-1], axis=(1))
#        
#premInc = policies.p['POLPRTOT'][:,np.newaxis,np.newaxis] * policies.un
## JO premium charge de 20% CHIFFRE EN DUR A MODIFIER !!!
#rencours = (premInc * (1-timelastp)/policies.fractionnement()) * (1-0.2)
#condlist = [timelastp == 0, timelastp != 0]
#choicelist = [rencours == 0 , rencours]
#rencours=np.select(condlist, choicelist)
        
        



txsin = hyp.fraisVisite()
primcpl = ((policies.zeros() + 60)/policies.fractionnement()) * txsin * FU.mypayement(policies) * FU.inforceSM(policies)
primcpl = primcpl * FU.isactive(policies)