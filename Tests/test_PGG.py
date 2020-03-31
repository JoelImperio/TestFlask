import numpy as np
import pandas as pd
import unittest as ut
import coverage
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
from Produits import FU,AX,HO,PR

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

RTOL=0.1
ATOL=1
decimalPrecision=2

#Ne marche pas pour les premiums d'AX
# RTOL=0.0001
# ATOL=0.001
# decimalPrecision=2



#Test spécifique produit pour le Best Estimate et la PGG
class Test_FU(ut.TestCase):

    
    spProphet = DataProphet['FU'].replace('-',0)
    sp=FU()

    def test_nombrePolices(self):
        nbrPolices=3392
        self.assertEqual(len(self.sp.p),nbrPolices)

    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
            

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalCommissions ERROR')


            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:408,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')
            

    def test_PGG(self):
        
        prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Fun']),'PGG'].values[0]
        
        python=self.sp.PGG().values[0,0]
        
        self.assertEqual(round(prophet,decimalPrecision),round(python,decimalPrecision))       


#Test spécifique produit pour le Best Estimate et la PGG
class Test_AX(ut.TestCase):

    
    spProphet = DataProphet['AX'].replace('-',0)
    sp=AX()

    def test_nombrePolices(self):
        nbrPolices=2054
        self.assertEqual(len(self.sp.p),nbrPolices)

    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
            

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalCommissions ERROR')


            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:408,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')
            

    def test_PGG(self):
        
        prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Axiprotect']),'PGG'].values[0]
        
        python=self.sp.PGG().values[0,0]
        
        self.assertEqual(round(prophet,decimalPrecision),round(python,decimalPrecision))       


#Test spécifique produit pour le Best Estimate et la PGG
class Test_HO(ut.TestCase):

    
    spProphet = DataProphet['HO'].replace('-',0)
    sp=HO()

    def test_nombrePolices(self):
        nbrPolices=1395
        self.assertEqual(len(self.sp.p),nbrPolices)

    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
            

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalCommissions ERROR')


            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:408,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')
            

    def test_PGG(self):
        
        prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Hospitalis']),'PGG'].values[0]
        
        python=self.sp.PGG().values[0,0]
        
        self.assertEqual(round(prophet,decimalPrecision),round(python,decimalPrecision))  

#Test spécifique produit pour le Best Estimate et la PGG
class Test_PR(ut.TestCase):

    
    spProphet = DataProphet['PR'].replace('-',0)
    sp=PR()

    def test_nombrePolices(self):
        nbrPolices=260
        self.assertEqual(len(self.sp.p),nbrPolices)

    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
            

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalCommissions ERROR')


            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:408,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')
            

    def test_PGG(self):
        
        prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Preciso']),'PGG'].values[0]
        
        python=self.sp.PGG().values[0,0]
        
        self.assertEqual(round(prophet,decimalPrecision),round(python,decimalPrecision)) 





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
