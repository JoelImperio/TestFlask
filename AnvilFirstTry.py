# pip install anvil-uplink



import anvil.server
import anvil.media
import pandas as pd


#Connect to Uplink
anvil.server.connect("3ZKB3TT2SZ7CKNXGTIXFLIB5-7SANNLTDTVUUVWY5")


# import app_tables to access your data tables
from anvil.tables import app_tables
from Produits import HO

  

files = [r['media_obj'] for r in app_tables.my_files.search()]

myliste=[]

for f in files:
    with anvil.media.TempFile(f) as filename:
        df = pd.read_excel(filename)
    
        myliste.append(df)

    

@anvil.server.callable
def runMyPGG():
    a=HO().PGG()
    app_tables.resultpgg.add_row(res=a.PGG[0], Produit=a.index[0])
#     return a
    
# a=runMyPGG()   

anvil.server.wait_forever()