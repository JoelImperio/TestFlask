import numpy as np
import pandas as pd
import unittest as ut
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))

    ### Importer script
from tryEpargnes import EP

start_time = time.time()



    ### Fichier résultat
#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet_JO.xls',sheet_name=None,skiprows=7)


#Celui-ci est générique ne pas modifier
#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)


#Test spécifique produit pour le Best Estimate et la PGG
class Test_EP(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester
    sp=EP()
    #sp.mod([10])
    length = len(sp.totalPremium()[0,:,0]) - 1
    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        
        # prophet=np.array(spProphet.loc[:length,'PREM_INC'].to_numpy(),dtype=float)
        
        
    ### La méthode à tester 'totalPremium()'
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')
       
        
       
     
    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')


        
    def test_DeathClaim(self):
        
    ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
    ### La méthode à tester 'totalPremium()'
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')


    def test_surrender(self):

        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')


    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')





    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
            
            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalExpense ERROR')
            



    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        

    # def test_PGG(self):
        
    #     prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['Fun']),'PGG'].values[0]
        
    #     python=self.sp.PGG().values[0,0]
        
    #     self.assertEqual(round(prophet,self.decimalPrecision),round(python,self.decimalPrecision))       


#Test spécifique pour une police pour le Best Estimate et la PGG
class Test_EP_28(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_28'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[28]
    
    sp=EP()
    sp.mod(polmod)
 
    length = len(sp.totalPremium()[0,:,0])-1
    
    
    
    
# =============================================================================
#     PRINCIPAUX VECTEUR A TESTER
# =============================================================================
    
    def test_Premium(self):
        
    ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
    ### La méthode à tester 'totalPremium()'
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        




# =============================================================================
# VECTEUR SECONDAIRE A TESTER
# =============================================================================



    def test_DeathClaim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')


    
    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')








class Test_EP_29(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_29'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[29]
    
    sp=EP()
    sp.mod(polmod)
    
    length = len(sp.totalPremium()[0,:,0])-1
    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')
        
        
# =============================================================================
#    PRINCIPAUX VECTEUR     
# =============================================================================
        
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')


        
        
    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        
# =============================================================================
#      Vecteur secondaires   
# =============================================================================
        
        
    def test_DeathClaim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')





class Test_EP_30(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_30'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[30]
    
    sp=EP()
    sp.mod(polmod)
    
    length = len(sp.totalPremium()[0,:,0])-1
    
# =============================================================================
#    PRINCIPAUX VECTEUR     
# =============================================================================
        
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')


        
    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        
        
        
# =============================================================================
# VECTEUR SECONDAIRE        
# =============================================================================
        
        
    def test_DeathClaim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')






class Test_EP_31(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_31'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[31]
    
    sp=EP()
    sp.mod(polmod)
    
    length = len(sp.totalPremium()[0,:,0])-1
    
# =============================================================================
#    PRINCIPAUX VECTEUR     
# =============================================================================
        
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')


    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
         
      
# =============================================================================
#      VECTEURS SECONDAIRES  
# =============================================================================
 
    def test_DeathClaim(self):
        
    ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
    ### La méthode à tester 'totalPremium()'
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')







class Test_EP_32(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_32'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[32]
    
    sp=EP()
    sp.mod(polmod)
    
    length = len(sp.totalPremium()[0,:,0])-1
    
# =============================================================================
#    PRINCIPAUX VECTEUR     
# =============================================================================
        
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        
# =============================================================================
# VECTEURS SECONDAIRES
# =============================================================================
        
        
    def test_DeathClaim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')





class Test_EP_33(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_33'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[33]
    
    sp=EP()
    sp.mod(polmod)
    
    length = len(sp.totalPremium()[0,:,0])-1
    
# =============================================================================
#    PRINCIPAUX VECTEUR     
# =============================================================================
        
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        
# =============================================================================
#     VECTEUR SECONDAIRES    
# =============================================================================
        
        
        
    def test_DeathClaim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)

        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')





class Test_EP_36(ut.TestCase):

    RTOL=0.0001
    ATOL=0.001
    decimalPrecision=2
    
    ### Onglet fichier résultat 
    ongletResultat='EP_36'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[36]
    
    sp=EP()
    sp.mod(polmod)
    
    length = len(sp.totalPremium()[0,:,0])-1
    
# =============================================================================
#    PRINCIPAUX VECTEUR     
# =============================================================================
        
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalClaim ERROR')
           


    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalCommissions ERROR')



    def test_expenses(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalExpense())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='BEL ERROR')
            
        
        
# =============================================================================
#    VECTEURS SECONDAIRES
# =============================================================================
        
    def test_DeathClaim(self):

        prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.deathClaim())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




    def test_surrender(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.surrender())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')



    def test_maturity(self):

        prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.maturity())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = self.RTOL, atol = self.ATOL, err_msg='totalPremium ERROR ')




### Lancer mes tests
ut.main()



### Lancer tous les tests

# loader = ut.TestLoader()
# suite = loader.discover('.')
# runner = ut.TextTestRunner()
# runner.run(suite)

print("Tests--- %s sec" %'%.2f'%  (time.time() - start_time))