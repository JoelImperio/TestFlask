# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 01:00:49 2019

@author: Robin
"""


#Exemple vectorisation
vgetFraisFractionement=np.vectorize(getFraisFractionement,excluded=['dfs'])
mvtn['FraisFractionement']=vgetFraisFractionement(moda=(mvtn['POLMOD'].to_numpy()),frac=(mvtn['Fractionmt'].to_numpy()), dfs=ff)

