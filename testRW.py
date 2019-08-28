from iPortfolio import portfolio
from iHypothesis import hypo
import numpy as np
import pandas as pd
import time

a=portfolio.ids([301,2501])
b=portfolio.mod([8,9])
c=portfolio.tout

hyp=hypo([2,5])
d=hyp.lapse()
e=hyp.run

f=a.iloc[:,1:5].to_numpy()
g=np.ones([2,1])
h=f+g
i=h+1


a=pd.DataFrame(100,100)




start_time = time.time()
for i in range(100):
    z=c[0]+c[1]
print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))

start_time = time.time()
for i in range(100):
    zz=c[0].to_numpy() + c[1].to_numpy()
    zz=pd.DataFrame(zz)
print("additionNumpy--- %s seconds ---" %'%.20f'%  (time.time() - start_time))
