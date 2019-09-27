import numpy as np
import pandas as pd
import time

import os, os.path
from Portefeuille import Portfolio
from Parametres import Hypo

from MyPyliferisk import MortalityTable,qx
from MyPyliferisk.mortalitytables import EKM05i


tariff = MortalityTable(nt=EKM05i)

print(tariff.qx[50])
t = 0
pd.to_datetime(t.astype(str), format='%Y%m%d').dt.date