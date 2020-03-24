import numpy as np
import pandas as pd
import unittest as ut
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

    ### Importer script
from tryMixtes import MI

start_time = time.time()



    ### Fichier résultat
#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet.xls',sheet_name=None,skiprows=7)


#Celui-ci est générique ne pas modifier
#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)


#Test spécifique produit pour le Best Estimate et la PGG
class Test_MI(ut.TestCase):

    RTOL=0.1
    ATOL=1
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='MI'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester
    sp=MI()
    #sp.mod([10])
    
    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
    ### La méthode à tester 'totalPremium()'
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')
            

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
            


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')


            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:408,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalExpense ERROR')
            


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:408,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            

    # def test_PGG(self):
        
    #     prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Fun']),'PGG'].values[0]
        
    #     python=self.sp.PGG().values[0,0]
        
    #     self.assertEqual(round(prophet,self.decimalPrecision),round(python,self.decimalPrecision))       


#Test spécifique pour une police pour le Best Estimate et la PGG
class Test_MI_POLICE(ut.TestCase):

    RTOL=0.1
    ATOL=1
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='MI_POLICE'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polnum=[301]
    
    sp=MI()
    sp.ids(polnum)

    
    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:408,'PREM_INC'].to_numpy(),dtype=float)
        
    ### La méthode à tester 'totalPremium()'
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')
            


### Lancer mes tests
ut.main()



### Lancer tous les tests

# loader = ut.TestLoader()
# suite = loader.discover('.')
# runner = ut.TextTestRunner()
# runner.run(suite)

print("Tests--- %s sec" %'%.2f'%  (time.time() - start_time))