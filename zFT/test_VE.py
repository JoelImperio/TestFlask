import numpy as np
import pandas as pd
import unittest as ut
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

    ### Importer script
from tryVieEntière import VE

start_time = time.time()



    ### Fichier résultat
#L'ensemble des variables Prophet par produit
DataProphet = pd.read_excel(path+'\Resultats_Prophet_VE.xls',sheet_name = None,skiprows = 7)


#Celui-ci est générique ne pas modifier
#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG = pd.read_excel(path+'\Resultats_PGG.xls',sheet_name = 'Synthese',skiprows = 3)



    ### Précision souhaitée
RTOL = 0.0001
ATOL = 0.001
decimalPrecision = 2

# Test spécifique produit pour le Best Estimate et la PGG
class Test_VE(ut.TestCase):
    
    ### Onglet fichier résultat 
    ongletResultat = 'VE'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester
    sp = VE()
    sp.mod([11,1])

    length = len(sp.totalPremium()[0,:,0]) - 1

    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet = np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
    ### La méthode à tester 'totalPremium()'
        python = np.sum(self.sp.totalPremium()[:,:1190,0],axis=0)
        np.testing.assert_allclose(prophet, python, rtol=RTOL, atol=ATOL, err_msg='totalPremium ERROR ')
            
    def test_Claim(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        python = np.sum(self.sp.totalClaim()[:,:1190,0],axis=0,dtype=float)
        np.testing.assert_allclose(prophet, python, rtol=RTOL, atol=ATOL, err_msg='totalClaim ERROR')
            
    def test_Commissions(self):  
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        python = np.array(np.sum(self.sp.totalCommissions()[:,:1190,0],axis=0),dtype=float)
        np.testing.assert_allclose(prophet, python, rtol=RTOL, atol=ATOL, err_msg='totalCommissions ERROR')
      
    def test_Expense(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        python = np.sum(self.sp.totalExpense()[:,:1190,0],axis=0)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol=ATOL, err_msg='totalExpense ERROR')
            
    def test_BEL(self):
        prophet = np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        python = np.sum(self.sp.BEL()[:,:1190,0],axis=0)
        np.testing.assert_allclose(prophet, python, rtol=RTOL, atol=ATOL, err_msg='BEL ERROR')


class Test_MOD11(ut.TestCase): 
    ### Onglet fichier résultat 
    ongletResultat = 'MOD11'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester
    sp = VE()
    sp.mod([11])

    length = len(sp.totalPremium()[0,:,0]) - 1

    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet = np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype = float)
        
    ### La méthode à tester 'totalPremium()'
        python = np.sum(self.sp.totalPremium()[:,:1190,0],axis = 0) 
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalPremium ERROR ')
            
    def test_Claim(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype = float)
        python = np.sum(self.sp.totalClaim()[:,:1190,0],axis = 0,dtype = float)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalClaim ERROR')
            
    def test_Commissions(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype = float)
        python = np.array(np.sum(self.sp.totalCommissions()[:,:1190,0],axis = 0),dtype = float)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalCommissions ERROR')
    
    def test_Expense(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype = float)
        python = np.sum(self.sp.totalExpense()[:,:1190,0],axis = 0)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalExpense ERROR')
            
    def test_BEL(self):
        prophet = np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype = float)
        python = np.sum(self.sp.BEL()[:,:1190,0],axis = 0)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'BEL ERROR')         


class Test_MOD01(ut.TestCase):
    
    ### Onglet fichier résultat 
    ongletResultat = 'MOD01'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester
    sp = VE()
    sp.mod([1])

    length = len(sp.totalPremium()[0,:,0]) - 1

    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet = np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype = float)
        
    ### La méthode à tester 'totalPremium()'
        python = np.sum(self.sp.totalPremium()[:,:1164,0],axis = 0)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalPremium ERROR ')
            
    def test_Claim(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype = float)
        python = np.sum(self.sp.totalClaim()[:,:1164,0],axis = 0,dtype = float)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalClaim ERROR')

    def test_Commissions(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype = float)
        python = np.array(np.sum(self.sp.totalCommissions()[:,:1164,0],axis = 0),dtype = float)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalCommissions ERROR')
     
    def test_Expense(self):
        prophet = np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype = float)
        python = np.sum(self.sp.totalExpense()[:,:1164,0],axis = 0)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'totalExpense ERROR')

    def test_BEL(self):
        prophet = np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype = float)
        python = np.sum(self.sp.BEL()[:,:1164,0],axis = 0)
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg = 'BEL ERROR')    


### Lancer mes tests
ut.main()



### Lancer tous les tests

# loader = ut.TestLoader()
# suite = loader.discover('.')
# runner = ut.TextTestRunner()
# runner.run(suite)

print("Tests--- %s sec" %'%.2f'%  (time.time() - start_time))