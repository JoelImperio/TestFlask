import numpy as np
import pandas as pd
import time

import os, os.path
from Portefeuille import Portfolio
from Parametres import Hypo

from MyPyliferisk import MortalityTable,vqx,qx
from MyPyliferisk.mortalitytables import EKM05i



tariff = MortalityTable(nt=EKM05i)



vtariff = np.vectorize(tariff.qx()) 

u = np.arange(10).astype(int)


