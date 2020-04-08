#!/usr/bin/python
# Instructions:
# - Important: The first item indicate the age when the table starts.
# - The probability is qx * 1000.

import pandas as pd
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
 

df=pd.ExcelFile(path  + '/TablesMortalite.xlsx').parse("Tables")
df=df.fillna(1)


def getMT(mt):
    mt=mt.tolist()
    mt[0]=int(mt[0])
    mt=tuple(mt)
    return mt

#Voici la liste des tables de mortalité qui se trouve dans le fichier excel 'TableMortalite.xlsx'

EKM05i=getMT(df['EKM05i'])
EKF05_2ordre=getMT(df['EKF05_2ordre'])
EKM05_2ordre=getMT(df['EKM05_2ordre'])
EKF1995=getMT(df['EKF95'])
EKM1995=getMT(df['EKM95'])
EKF95_2ordre=getMT(df['EKF95_2ordre'])
EKM95_2ordre=getMT(df['EKM95_2ordre'])
GKF1995=getMT(df['GKF95'])
GKM1995=getMT(df['GKM95'])