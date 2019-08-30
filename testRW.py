from iPortfolio import Portfolio
from iHypothesis import Hypo
from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKF95_2ordre
from ModX import MODX
import numpy as np
import pandas as pd
import time

#policies=Portfolio()
#a=policies.mod([2])
#b=policies.ids([301,2501,3101])
#c=policies.p



table=EKF95_2ordre
age=35
mt=MortalityTable(nt=table)

b=qx(mt,age)


#start_time = time.time()
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))



#class A:
#    def __init__(self,a,b):
#        self.a=a
#        self.b=b
#        self.tag=self.add(self.a,self.b)
#    def add(self,a,b):
#        return a+b
#    
#
#class B(A):
#    def adds(self,a,b):
#        return a
#    
#a=A(1,2).tag
#b=B(0,0).tag
