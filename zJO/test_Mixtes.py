import numpy as np
import pandas as pd
import unittest as ut
import coverage
import time
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))







start_time = time.time()

    ### Importation Data tests
from tryMixtes import MI
#L'ensemble des variables Prophet par produit
DataProphet=pd.read_excel(path+'\Resultats_Prophet_Mixtes.xls',sheet_name=None,skiprows=7)

#Les resultats de la PGG selon la répartition en vigueur
ResultatPGG=pd.read_excel(path+'\Resultats_PGG.xls',sheet_name='Synthese',skiprows=3)


    ### Test Couverture Start
# cov=coverage.Coverage()
# cov.start()

# sp=MI()
    ### Précision souhaitée
RTOL=0.0001
ATOL=0.001
decimalPrecision=2

#Test spécifique produit pour le Best Estimate et la PGG
class Test_MI(ut.TestCase):

    ### Onglet fichier résultat 
    ongletResultat='MI'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Sous portefeuille à tester

    polmod=[2,6,7,10]
    
    sp=MI()
    sp.mod(polmod)
    

    length = len(sp.totalPremium()[0,:,0]) - 1
    

    # def test_nombrePolices(self):
    #     nbrPolices=877
    #     self.assertEqual(len(self.sp.p),nbrPolices)
    
    
    def test_Premium(self):
        
        ### La variable à tester 'PREM_INC'
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        
        ### La méthode à tester 'totalPremium()'
        python=np.sum(self.sp.totalPremium()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalPremium ERROR ')
       
        
       
     
    def test_Commissions(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_COMM'].to_numpy(),dtype=float)
        
        python=np.array(np.sum(self.sp.totalCommissions()[:,:409,0],axis=0),dtype=float)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalCommissions ERROR')




    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            
            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            



    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')

            
    def test_PGG(self):

        python=np.array(self.sp.PGG().to_numpy(),dtype=float)
        python= np.squeeze(python)         
                
        prophet=ResultatPGG.loc[ResultatPGG['Prophet'].isin(['M0','M0.25','M0.5','M0.75','M1','M1.25','M1.75','M2.5','M2','M3.5']),'PGG']
        prophet=np.array(prophet[0:len(python)].to_numpy(),dtype=float)
        np.testing.assert_allclose(np.around(prophet,decimals=decimalPrecision),np.around(python,decimals=decimalPrecision), rtol = RTOL, atol = (decimalPrecision/(decimalPrecision*100)), err_msg='PGG ERROR')
       



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
            




#Test spécifique pour une police pour le Best Estimate et la PGG
class Test_MOD_10(ut.TestCase):

    
    ### Onglet fichier résultat 
    ongletResultat='MOD10'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    
    ### Police à tester
    polmod=[10]
    
    sp=MI()
    sp.mod(polmod)
 
    length = len(sp.nbrPolIf[0,:,0])-1
    
    
# =============================================================================
#     PRINCIPAUX VECTEUR A TESTER
# =============================================================================

    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='Premium ERROR ')    


    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
        
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
        
    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')

            

# =============================================================================
# VECTEUR SECONDAIRE A TESTER
# =============================================================================

    # def test_nbPolif(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'NO_POLS_IF'].to_numpy(),dtype=float)
        
    #     python=np.sum((self.sp.nbrPolIf)[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='NbrPolif ERROR ')






    # def test_princpalClaim(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimPrincipal()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            

    # def test_claimCompl(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'RIDERC_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimCompl()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='RIDERC OUTGO ERROR')
            


    # def test_maturity(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.maturity()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='maturity outgo ERROR')
            
    # def test_surrender(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.surrender()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='surrender outgo ERROR')
            




class Test_MOD_2_1(ut.TestCase):

    
    ### Onglet fichier résultat 
    ongletResultat='MOD2_1'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    

    sp=MI()
    sp.modHead([2],1)
 
    length = len(sp.nbrPolIf[0,:,0])-1
    
    
# =============================================================================
#     PRINCIPAUX VECTEUR A TESTER
# =============================================================================
    
    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='Premium ERROR ')

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
        
        
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            

    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')
# =============================================================================
# VECTEUR SECONDAIRE A TESTER
# =============================================================================

    # def test_nbPolif(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'NO_POLS_IF'].to_numpy(),dtype=float)
        
    #     python=np.sum((self.sp.nbrPolIf)[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='NbrPolif ERROR ')




    # def test_princpalClaim(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimPrincipal()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            
    # def test_claimCompl(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'RIDERC_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimCompl()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='RIDERC OUTGO ERROR')
            
    # def test_maturity(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.maturity()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='maturity outgo ERROR')
            
    # def test_surrender(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.surrender()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='surrender outgo ERROR')
            


class Test_MOD_2_2(ut.TestCase):

    
    ### Onglet fichier résultat 
    ongletResultat='MOD2_2'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    

    sp=MI()
    sp.modHead([2],2)
 
    length = len(sp.nbrPolIf[0,:,0])-1
    
    
# =============================================================================
#     PRINCIPAUX VECTEUR A TESTER
# =============================================================================
    

    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='Premium ERROR ')

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
        
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            
    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')
# =============================================================================
# VECTEUR SECONDAIRE A TESTER
# =============================================================================

    # def test_nbPolif(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'NO_POLS_IF'].to_numpy(),dtype=float)
        
    #     python=np.sum((self.sp.nbrPolIf)[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='NbrPolif ERROR ')



    # def test_Premium(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
    #     python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='Premium ERROR ')



    # def test_princpalClaim(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimPrincipal()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            

    # def test_claimCompl(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'RIDERC_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimCompl()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='RIDERC OUTGO ERROR')
            
    # def test_maturity(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.maturity()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='maturity outgo ERROR')
            
    # def test_surrender(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.surrender()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='surrender outgo ERROR')
            
    # def test_Claim(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')

class Test_MOD_6_7(ut.TestCase):

    
    ### Onglet fichier résultat 
    ongletResultat='MOD6_7'
    spProphet = DataProphet[ongletResultat].replace('-',0)
    

    sp=MI()
    sp.mod([6,7])
 
    length = len(sp.nbrPolIf[0,:,0])-1
    
    
# =============================================================================
#     PRINCIPAUX VECTEUR A TESTER
# =============================================================================
    

    def test_Premium(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'PREM_INC'].to_numpy(),dtype=float)
        
        python=np.sum((self.sp.totalPremium())[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='Premium ERROR ')

    def test_Claim(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_PREST'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalClaim()[:,:409,0],axis=0)

        
        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
        
            
    def test_Expense(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'TOT_EXP'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.totalExpense()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalExpense ERROR')
            
    def test_BEL(self):
        
        prophet=np.array(self.spProphet.loc[:self.length,'BEL_B'].to_numpy(),dtype=float)
        
        python=np.sum(self.sp.BEL()[:,:409,0],axis=0)

        np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='BEL ERROR')

# =============================================================================
# VECTEUR SECONDAIRE A TESTER
# =============================================================================

    # def test_nbPolif(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'NO_POLS_IF'].to_numpy(),dtype=float)
        
    #     # prophet=np.array(spProphet.loc[:length,'NO_POLS_IF'].to_numpy(),dtype=float)
        
    #     python=np.sum((self.sp.nbrPolIf)[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='NbrPolif ERROR ')




    # def test_princpalClaim(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'DEATH_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimPrincipal()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='totalClaim ERROR')
            

    # def test_claimCompl(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'RIDERC_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.claimCompl()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='RIDERC OUTGO ERROR')
            

    # def test_maturity(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'MAT_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.maturity()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='maturity outgo ERROR')
            

    # def test_surrender(self):
        
    #     prophet=np.array(self.spProphet.loc[:self.length,'SURR_OUTGO'].to_numpy(),dtype=float)
        
    #     python=np.sum(self.sp.surrender()[:,:409,0],axis=0)

    #     np.testing.assert_allclose(prophet, python, rtol = RTOL, atol = ATOL, err_msg='surrender outgo ERROR')
            



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