from Portefeuille.Portfolio import portfolio
from Hypotheses.Hypothesis import hypo
import numpy as np

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