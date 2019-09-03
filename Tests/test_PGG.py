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

DataProphet=pd.ExcelFile(path+'/Tests\DataProphet.xls',skiprows=5).parse("Hypothèses")

pTest=pd.read_csv(path+'/Tests\Portfolio_Test.csv')

pTest=portfolioPreProcessing(pTest)

hTest=pd.ExcelFile(path  + '/Tests/TablesProphet 2018-12_Test.xls').parse("Hypothèses")


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




