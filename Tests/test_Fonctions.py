# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 18:46:59 2019

@author: Robin
"""

#- Chaque fonction qui est crée doit faire l'objet d'un test
#- But 100% de couverture du code 

import unittest
import numpy as np
import pandas as pd


a = np.array([1,2,3,4,5,6,7,8,9,10])
b = a+1.99


df1=pd.DataFrame({'a':[1,2,3,4,5]})
df2=pd.DataFrame({'a':[6,7,8,9,10]})

df3=df1.to_numpy()
df4=df2.to_numpy()


unittest.main()



class MyTest3(unittest.TestCase):
    def test6(self):
        expected_res=pd.Series([7,9,11,13,15])
        pd.testing.assert_series_equal((df1['a']+df2['a']),expected_res,check_names=False)


    def test7(self):
        expected_res=pd.DataFrame({'b':[7,9,11,13,15]}).to_numpy()
        np.testing.assert_allclose((df3+df4), expected_res, rtol = RTOL, atol = ATOL, err_msg='MySecondError')
        
        
class MyTest2(unittest.TestCase):
    def test2(self):        
        self.assertEqual(a.tolist(),b.tolist()) 

    def test3(self):
        abserreur=2
        relativerreur=0.1
        c=a-b
        f=(a-b)/b
        d=abs(c.max())
        e=abs(c.sum())
        g=abs(f.max())
        assert (d<abserreur) & (e<len(c)*abserreur) & (g<relativerreur) 
        
    def test4(self):
        abserreur=5
        relativerreur=0.2
        c=a-b
        f=(a-b)/b
        d=abs(c.max())
        e=abs(c.sum())
        g=abs(f.max())
        h=np.abs(np.around(a-b,0))-1
        i=h.max()
        self.assertLess(d, abserreur)
        self.assertLess(e, len(c)*abserreur)
        self.assertLess(g, relativerreur)
        self.assertEqual(i,0)
    
    def test5(self):
        abserreur=2
        relativerreur=0.2
        c=a-b
        f=(a-b)/b
        d=abs(c.max())
        e=abs(c.sum())
        g=abs(f.max())
        assert (d<abserreur)
        assert (e<len(c)*abserreur)
        assert (g<relativerreur)
