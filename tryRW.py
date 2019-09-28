import numpy as np
import pandas as pd
import time

from Portefeuille import Portfolio
from Parametres import Hypo

from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import EKM05i


policies=Portfolio()
#hyp=Hypo(shape=policies.shape)
#policies.ids([301])


#def myQx(age):
#    
#    mt=MortalityTable(nt=EKM05i, perc=100)
#    myQx=qx(mt,int(age))
#    return myQx
#
#
#
#vQx=np.vectorize(myQx)
#myAge=policies.age1()
#myvQx=policies.un
#myvQx=vQx(age=myAge)



#lut = np.arange(256)
#image = np.random.randint(256, size=(5000, 5000))
#a=np.take(lut, image)
#np.all(lut[image] == np.take(lut, image))



#start_time = time.time()
#
#
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))



#tariff = MortalityTable(nt=EKM05i)
#experience = MortalityTable(nt=EKM05i, perc=85)

def qx(table=EKM05i, exp=100):
    mt=MortalityTable(nt=table, perc=exp)
    aQx=pd.DataFrame(mt.qx).to_numpy()
    myAge=(policies.age1()).astype(int)
    return np.take(aQx,myAge)

a=qx()


#def myQx(age):
#    mt=MortalityTable(nt=EKM05i, perc=100)
#    aQx=pd.DataFrame(mt.qx)     
#    return aQx.iloc[int(age)]
#
#vQx=np.vectorize(myQx)
#myAge=policies.age1()
#myvQx=policies.un
#myvQx=vQx(age=myAge)


