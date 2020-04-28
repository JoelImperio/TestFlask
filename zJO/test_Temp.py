# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import unittest as ut
import coverage
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))


    ### Importer script
from tryTemporaires import TE




start_time = time.time()


#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet_Temp.xls',sheet_name=None,skiprows=7)

#Les resultats de la PGG selon la répartition en vigueur
# ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)


    ### Test Couverture Start
# cov=coverage.Coverage()
# cov.start()

# sp=MI()
    ### Précision souhaitée
RTOL=0.0001
ATOL=0.001
decimalPrecision=2

#Test spécifique produit pour le Best Estimate et la PGG
class Test_TEMP(ut.TestCase):

    ### Onglet fichier résultat 
    ongletResultat='TEMP'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester

    polmod=[4,3]
    
    sp=TE()
    sp.mod(polmod)
    

    length = len(sp.totalPremium()[0,:,0]) - 1
    

    # def test_nombrePolices(self):
    #     nbrPolices=877
    #     self.assertEqual(len(self.sp.p),nbrPolices)
    
    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)

        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
       

     
    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalCommissions ERROR')



    # def test_Claim(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            
            
    # def test_Expense(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            



    # def test_BEL(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')

            
    # def test_PGG(self):

    #     python=np.array(self.sp.PGG().to_numpy(),dtype=float)
    #     python= np.squeeze(python)         
                
    #     prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['M0','M0.25','M0.5','M0.75','M1','M1.25','M1.75','M2.5','M2','M3.5']),'PGG']
    #     prophet=np.array(prophet[0:len(python)].to_numpy(),dtype=float)
    #     np.testing.assert_allclose(np.around(prophet,decimals=decimalPrecision),np.around(python,decimals=decimalPrecision), rtol = RTOL, atol = (decimalPrecision/(decimalPrecision*100)), err_msg='PGG ERROR')
       


    def test_ClaimCompl(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'RIDERC_OUTGO'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.claimCompl()[:,:409,0],axis=0),dtype=float)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='riderCoutgo ERROR')





# #Test spécifique pour une police pour le Best Estimate et la PGG
# class Test_MI_POLICE(ut.TestCase):
    
#     ### Onglet fichier résultat 
#     ongletResultat='MI_POLICE'
#     spProphet = DataProphet[ongletResultat].replace('-',0)
    
#     ### Police à tester
#     polnum=[301]
    
#     sp=MI()
#     sp.ids(polnum)

#     length = len(sp.totalPremium()[0,:,0]) - 1
    
#     def test_Premium(self):
        
#     ### La variable à tester 'PREM_INC'
#         prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
#     ### La méthode à tester 'totalPremium()'
#         python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
#         np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
            






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