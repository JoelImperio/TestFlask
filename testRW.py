from iPortfolio import Portfolio
from iHypothesis import Hypo
from ModX import mod8
import numpy as np
import pandas as pd
import time

policies=Portfolio()
a=policies.ids([301,2501,3101])
b=policies.mod([8,9])
c=policies.p

#hyp=Hypo([2,5])
#d=hyp.lapse()
#e=hyp.run
#
#f=a.iloc[:,1:5].to_numpy()
#g=np.ones([2,1])
#h=f+g
#i=h+1





#start_time = time.time()
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))



class A:
    def __init__(self,a,b):
        self.a=a
        self.b=b
        self.tag=self.add(self.a,self.b)
    def add(self,a,b):
        return a+b
    

class B(A):
    def adds(self,a,b):
        return a
    
a=A(1,2).tag
b=B(0,0).tag
