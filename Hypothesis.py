# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 18:29:45 2019

@author: Robin
"""

#Tables :
#-	Actu
#-	Paramfrais: 2 types de frais
#-	Global:mortalité d’expérience, sensibilité aux rachat, taux d’inflation
#-	Rdt-est: taux de PB
#-	Rachat: taux de rachat
#-	Reducs: taux de réduction
#-	Paramgticompl: taux de sinistralité
#-	Paramcomm: commissions ? ou directement dans le portfolio ?
#-  Date de calcul
#
#- Il y a les inputs en lien avec le run 
#- Il y a des inputs généraux

#class hypo:
#    ba=5
#    def __init__(self):
#        self.ba=10
#    def Lapse(a):
#        return print(float(a))
#    def Cost(a):
#        return print(float(a))
#    def Rate(a):
#        return print(float(a))
#    def run(a,self):
#        return print(float(a) + self.ba)
#    
#    
#c=hypo()
#c=hypo.run(1,c)
#d=hypo.ba
#e=hypo().ba
        
ba=6

class hypo:
    ba=5
    def __init__(self):
        self.ba=10
    def Lapse(a):
        return print(float(a))
    def Cost(a):
        return print(float(a))
    def Rate(a):
        return print(float(a))
    def run(a):
        return print(float(a) + ba)
    
    
#c=hypo()
c=hypo.run(1)
d=hypo.ba
e=hypo().ba










