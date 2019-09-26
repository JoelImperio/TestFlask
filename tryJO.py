import numpy as np
import pandas as pd
import time

from Portefeuille import Portfolio
from Parametres import Hypo

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i


tariff = MortalityTable(nt=EKM05i)

print(tariff.qx[50])

#Je suis dans Jo's branche