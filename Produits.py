from Portefeuille import Portfolio
import pandas as pd
import numpy as np
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

##############################################################################################################################
##############################################################################################################################


##############################################################################################################################
#Ceci est une class d'exemple pour reprendre merci de ne pas toucher
##############################################################################################################################
class MODEL(Portfolio):
    mods=[8,9]
    
    def __init__(self):
        super().__init__()
        self.p=self.mod(self.mods)



##############################################################################################################################
##############################################################################################################################