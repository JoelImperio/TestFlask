import numpy as np
import pandas as pd
import unittest as ut
import coverage
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i

from Portefeuille import Portfolio
from Parametres import Hypo, portfolioPreProcessing
from Produits import FU


#Importation des données pour les tests

#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet.xls',sheet_name=None,skiprows=7)
DataProphet=pd.concat(DataProphet,axis=1)


#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)

#Les variables de contrôle
variablesTest=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='AllVariablesTest',skiprows=7)

#Portefeuille servant de test qui correspond on portefeuille au 31.12.2018
pTest=pd.read_csv(path+'\Portfolio_Test.csv')
pTest=portfolioPreProcessing(pTest)

#Hypothèses servant de test qui correspond à celles en vigueur au 31.12.2018
hTest=pd.ExcelFile(path  + '/TablesProphet 2018-12_Test.xls').parse("Hypotheses")


#Instenciation Des Class pour les tests

pt=Portfolio(po=pTest)
ht=Hypo(hy=hTest,MyShape=pt.shape)

cov=coverage.Coverage()
cov.start()

#Test général sur la structure et la cohérence du modèle
class TestCoherenceGlobale(ut.TestCase):
    
    
#Ce test permet de vérifier que le nombre de polices chargées est correct par rapport à la clôture
    def test_nombrePolices(self):
        NombreTotalDePolices=9248
        self.assertEqual(len(Portfolio().p),NombreTotalDePolices)
        
    def test_Exemple(self):
        
        RTOL=0.1
        ATOL=1
        
        resultatAttendu=variablesTest['M_DISC_B']
        
        resultatScript=ht.rate()[0,:,0]
        
        np.testing.assert_allclose(resultatScript, resultatAttendu, rtol = RTOL, atol = ATOL, err_msg='Message Erreur')
        
    


#Test spécifique au produit X
class TestResultatsFUe(ut.TestCase):

    DataProphetMOD8_9 = DataProphet.filter(regex='MOD8_9')
    
    def test_Premium(self):
        premiumAttendus=DataProphetMOD8_9['PREM_INC']



#Print les tests et la couverture

loader = ut.TestLoader()
suite = loader.discover('.')
runner = ut.TextTestRunner()
runner.run(suite)

#ut.main()
cov.stop
cov.save
cov.report()



