from Portefeuille import Portfolio
from Parametres import Hypo

import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i

import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

#Importation d'une intance de Portfolio
p=Portfolio()



class myHypo(Hypo):

        def __init__(self):
            super().__init__()
            


class myFU(Portfolio):
    mods=[8,9]
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)
        self.ageMax=65

#Durée du contrat en mois
    def polTermM(self):
        
        entryAge1= self.p['Age1AtEntry'].to_numpy()
        
        entryAge2=self.p['Age2AtEntry'].to_numpy()
        
        entryAge2[entryAge2==999]=0
        ageAtEntry=np.maximum(entryAge1,entryAge2)
        
        #Nous pensons que cette variante est plus correct car dans le mod 9 la police continue jusqu'à 65 ans du plus jeune assuré
        #Il faut ajouté le code commenté pour prendre en compte le changement
#        mod=self.p['PMBMOD'].to_numpy()        
#        entryAge2[entryAge2==0]=999
#        ageAtEntry[mod==9]=np.minimum(entryAge1[mod==9],entryAge2[mod==9])
        
        
        ageAtEntry=ageAtEntry[:,np.newaxis,np.newaxis]*self.un
        
        ageTerm=self.ageMax*self.un
        
        polTerm=(ageTerm-ageAtEntry)*12

        return polTerm

#Retourn un 1 tant que la police est active et 0 lorsque dépasse le terme   
    def isActive(self):
        term=self.polTermM()
        dur=self.durationIf()
        
        active=self.un
        
        active[dur>term]=0
        
        return active
        

    def loop(self):
        
        nbrPolIf=self.un
        nbrDeath=self.zero
        nbrSurrender=self.zero
        nbrMaturities=self.zero
        nbrPolIfSM=self.zero
        
        for i in range(1,self.shape[1]):
            nbrPolIf=self.un
            nbrDeath=self.zero
            nbrSurrender=self.zero
            nbrMaturities=self.zero
            nbrPolIfSM=self.zero            
            
        
        return self
        


pol=myFU()
hyp=myHypo()


z=pol.ids([1107301])
#z=pol.mod([9])


a=pol.polTermM()
b=pol.isActive()
c=pol.durationIf()









#start_time = time.time()
#
#
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))









