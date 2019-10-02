import numpy as np
import pandas as pd
import time

import os, os.path
from Portefeuille import Portfolio
from Parametres import Hypo




# Python program for
# iterating array values
# using external loop
 



c = np.arange(10.)
print(c)
print(np.multiply(c[:-1], c[1:]/10, c[1:]))