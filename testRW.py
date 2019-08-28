from iPortfolio import portfolio
from iHypothesis import hypo
import numpy as np
import pandas as pd
import time

policies=portfolio()
a=policies.ids([301,2501,3101])
b=policies.mod([8,9])
c=policies.p

#hyp=hypo([2,5])
#d=hyp.lapse()
#e=hyp.run
#
#f=a.iloc[:,1:5].to_numpy()
#g=np.ones([2,1])
#h=f+g
#i=h+1





#start_time = time.time()
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))

