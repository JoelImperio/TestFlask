import numpy as np
import pandas as pd
import time

from iPortfolio import Portfolio
from iHypothesis import Hypo

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i

#from ModX import MODX


policies=Portfolio()
hyp=Hypo(shape=policies.shape,run=5)


a=policies.p
#b=policies.ids([301,2501,3101])
#c=policies.p





#mt=MortalityTable(nt=EKM05i)
#b=qx(mt,35)




#start_time = time.time()
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))

#test