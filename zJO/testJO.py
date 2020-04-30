# -*- coding: utf-8 -*-

from MyPyliferisk.mortalitytables import *



homme = Actuarial(nt=EKM1995, i=0, nbtete = 1)

qxM = homme.qx
lxM = homme.lx

for i in range(0,len(qxM)):
    
    qxM[i] = 0.005





    
    
    
    
test = Actuarial(q_x = qxM, i=0, nbtete = 1)
# test = Actuarial(nt=EKF1995, i=0, nbtete = 1)
test.qx

test.view()
