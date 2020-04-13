from MyPyliferisk import *
# from pyliferisk . mortalitytables import *
from MyPyliferisk import MortalityTable
from MyPyliferisk.mortalitytables import *



# table=EKM05i
# exp=100
# ass=1

# i = 0.05
x = 61
# n = 10
nt=Actuarial(nt=EKF95, i=0.0025)
# nt=MortalityTable(nt=EKM95000, i=0)

aQx=nt.qx


# test2 = annuity (nt , x, n, 0)

axb = annuity(nt,x,'w',0)
ax = annuity(nt,x,'w',1)


Mx = nt.Mx
Nx = nt.Nx
Dx = nt.Dx
lx = nt.lx
dx = nt.dx

# Nx = nt.Nx[61]

# adueval = Nx/Mx


qx = nt.qx[125]

age = 59

testMx = nt.Mx[age]
testDx = nt.Dx[age]
testNx = nt.Nx[age]

aatest = testNx / testDx


# D 0.97
# N 10.21