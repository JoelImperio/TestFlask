import numpy as np
import pandas as pd
import unittest as ut
import coverage
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


from iPortfolio import Portfolio, portfolioPreProcessing
from iHypothesis import Hypo

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i

from Mod8_9 import MOD8_9


#Importation des données pour les tests

#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet.xls',sheet_name=None,skiprows=7)
DataProphet=pd.concat(DataProphet,axis=1)


#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthèse',skiprows=3)

#Les variables de contrôle
variablesTest=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Test',skiprows=7)

#Portefeuille servant de test qui correspond on portefeuille au 31.12.2018
pTest=pd.read_csv(path+'\Portfolio_Test.csv')
pTest=portfolioPreProcessing(pTest)

#Hypothèses servant de test qui correspond à celles en vigueur au 31.12.2018
hTest=pd.ExcelFile(path  + '/TablesProphet 2018-12_Test.xls').parse("Hypothèses")


#Instenciation Des Class pour les tests

pt=Portfolio(po=pTest)
ht=Hypo(hy=hTest,MyShape=pt.shape, MyPortfolio=pt)


cov=coverage.Coverage()
cov.start()

#Test général sur la structure et la cohérence du modèle
class TestCoherenceGlobal(ut.TestCase):
    
    
#Ce test permet de vérifier que le nombre de polices chargées est correct par rapport à la clôture
    def test_nombrePolices(self):
        NombreTotalDePolices=9248
        self.assertEqual(len(Portfolio().p),NombreTotalDePolices)
        
#Ce test permet de vérifier que les taux de rendement sont corrects        
    def test_rate(self):
        self
        
        
    def test_Exemple(self):
        
        RTOL=0.1
        ATOL=1
        
        resultatAttendu=variablesTest['M_DISC_B']
        
        resultatScript=ht.rate()[0,:,0]
        
        np.testing.assert_allclose(resultatScript, resultatAttendu, rtol = RTOL, atol = ATOL, err_msg='Erreur')
        
    


#Test spécifique au produit X
class TestResultatsMod8_9(ut.TestCase):

    DataProphetMOD8_9 = DataProphet.filter(regex='MOD8_9')
    
    def test_inforce(self):
        self


#Print les tests et la couverture

ut.main()
cov.stop
cov.save
cov.report()



