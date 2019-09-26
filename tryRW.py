import numpy as np
import pandas as pd
import time

from Portefeuille import Portfolio
from Parametres import Hypo

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i


#policies=Portfolio()
#hyp=Hypo(shape=policies.shape)


#a=policies.p
#b=policies.ids([301,2501,3101])
#c=policies.p


#f=pd.Panel(e).to_frame().transpose()


#mt=MortalityTable(nt=EKM05i)
#b=qx(mt,35)




#start_time = time.time()
#print("additionPandas--- %s seconds ---" %'%.20f'%  (time.time() - start_time))

#test


tariff = MortalityTable(nt=EKM05i)
experience = MortalityTable(nt=EKM05i, perc=85)

# Print the omega (limiting age) of the both tables:

test1
test2
