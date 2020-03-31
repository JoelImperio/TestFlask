import numpy as np
import pandas as pd
import unittest as ut
import coverage
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
from Produits import FU,AX,HO,PR,EP

start_time = time.time()

    ### Importation Data tests

#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet.xls',sheet_name=None,skiprows=7)

#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)


    ### Test Couverture Start
# cov=coverage.Coverage()
# cov.start()


    ### Précision souhaitée

# RTOL=0.1
# ATOL=1
# decimalPrecision=2

RTOL=0.0001
ATOL=0.001
decimalPrecision=2

#Print les tests et la couverture

# cov.stop
# cov.save
# cov.report()
# ut.main()

print("Tests--- %s sec" %'%.2f'%  (time.time() - start_time))



    # def test_PGG(self):
sp=EP()

length = len(sp.totalPremium()[0,:,0]) - 1
        
prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Fun']),'PGG'].values[0]

python=self.sp.PGG().values[0,0]

self.assertEqual(round(prophet,decimalPrecision),round(python,self.decimalPrecision))       
