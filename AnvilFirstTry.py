# pip install anvil-uplink



import anvil.server
import anvil.media
import pandas as pd


#Connect to Uplink
anvil.server.connect("3ZKB3TT2SZ7CKNXGTIXFLIB5-7SANNLTDTVUUVWY5")


# import app_tables to access your data tables
from anvil.tables import app_tables

@anvil.server.callable
def get_people():
  people = app_tables.my_files.search()
  # for p in people:
  # 	print(f"This person's name is {p['name']}")
  # anvil.URLMedia("https://anvil.works/ide/img/banner-100.png")
  
  return people

# Call the server function 
# a=anvil.server.call('get_people')[0].url

# anvil.server.wait_forever()

# data_file_row = app_tables.my_files.get()
# data_file = data_file_row['media_obj']

# with anvil.media.TempFile(data_file) as filename:
#   df = pd.read_excel(filename, sheet_name='Hypothèses')
  


files = [r['media_obj'] for r in app_tables.my_files.search()]

myliste=[]

for f in files:
    with anvil.media.TempFile(f) as filename:
        df = pd.read_excel(filename)
    
        myliste.append(df)

    

# anvil.server.wait_forever()