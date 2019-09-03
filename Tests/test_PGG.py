import numpy as np
import pandas as pd
import unittest as ut
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


from iPortfolio import Portfolio, portfolioPreProcessing
from iHypothesis import Hypo

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i

from ModX import MODX
    


#Importation des données pour les tests

DataProphet=pd.read_excel(path+'\Resultats_Prophet.xls',sheet_name=None,skiprows=7)
DataProphet=pd.concat(DataProphet,axis=1)

ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthèse',skiprows=3)

pTest=pd.read_csv(path+'\Portfolio_Test.csv')
pTest=portfolioPreProcessing(pTest)

hTest=pd.ExcelFile(path  + '/TablesProphet 2018-12_Test.xls').parse("Hypothèses")


#Instenciation Des Class pour les tests

pt=Portfolio(po=pTest)
ht=Hypo(hy=hTest)


#Test général sur la structure et la cohérence du modèle
class TestCoherenceGlobal(ut.TestCase):

#Ce test permet de vérifier que le nombre de polices chargées est correct par rapport à la clôture
    def test_nombrePolices(self):
        NombreTotalDePolices=9248
        self.assertEqual(len(Portfolio().p),NombreTotalDePolices)
    


#Test spécifique au produit X
class TestResultatsModX(ut.TestCase):
    
    def test_inforce(self):
        self


ut.main()




