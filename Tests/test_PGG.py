import numpy as np
import pandas as pd
import unittest as ut
import coverage
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
from Produits import FU

start_time = time.time()

    ### Importation Data tests

#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet.xls',sheet_name=None,skiprows=7)

#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)


    ### Test Couverture Start
# cov=coverage.Coverage()
# cov.start()


#Test spécifique produit pour le Best Estimate
class Test_FU(ut.TestCase):

    RTOL=0.1
    ATOL=1
    
    spProphet = DataProphet['FU'].replace('-',0)
    sp=FU()

    def test_nombrePolices(self):
        nbrPolices=3392
        self.assertEqual(len(self.sp.p),nbrPolices)

    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='FU totalPremium ERROR')
            

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='FU totalClaim ERROR')
            


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='FU totalCommissions ERROR')


            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='FU totalExpense ERROR')
            


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:408,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='FU BEL ERROR')
            

    def test_PGG(self):
        
        prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Fun']),'PGG'].values[0]
        
        python=self.sp.PGG().values[0,0]
        
        decimals=2
        
        self.assertEqual(round(prophet,decimals),round(python,decimals))       



#Print les tests et la couverture

# cov.stop
# cov.save
# cov.report()
ut.main()

print("Tests--- %s sec" %'%.2f'%  (time.time() - start_time))

#Permet de lancer l'ensemble des test du workspace

# loader = ut.TestLoader()
# suite = loader.discover('.')
# runner = ut.TextTestRunner()
# runner.run(suite)
