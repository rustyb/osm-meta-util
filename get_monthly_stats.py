# combine stats from geojson.new files located in data/lesotho/.

# import required libraries
import os
import pandas as pd
import numpy as np

# read files in data folder for existing files:
def read_files(place="lesotho"):
	wd0 = 'data/'
	if place == 'lesotho':
		wd = wd0 + 'lesotho/'
	else:
		wd = wd0
	files = os.listdir (wd) # from /src
	fcheck = any (f.find ("lesotho") > -1 and f.endswith(".json.new") for f in files)
	if fcheck:
		json_files = [wd + i for i in files if i.endswith('.json.new')]
		print('Found %s geojson.new files in directory...' % len(json_files))
	else:
		sys.exit("make sure that json.new files exist in the data/lesotho directory.")
	return json_files

dfiles = read_files()

les0 = []
for f in dfiles:
	les0.append(pd.read_json(f))


lesa = pd.concat(les0)
print("Dataframe with %s rows x %s columns" % (lesa.shape[0], lesa.shape[1]))

lesa.timestamp = pd.to_datetime(lesa['timestamp']) # convert timestamp to date time index
lesa.set_index(lesa.timestamp, inplace=True)

apus = pd.read_csv('data/lesotho/app_unames.csv')
apps = apus.username[apus.is_app == 'Y']

print("Returning monthly stats for %s Assistant Planners" % len(apps))
les_apps = lesa[lesa.user.isin(apps.values)]

#results = les.groupby(['user']).changeset.nunique().unstack()
if len(les_apps) > 0:
	# get monthly count of unique changesets
	mon_un = les_apps.groupby(['user']).resample('M', how='nunique')[['changeset']] 
	mon_un.columns = ['unique_changesets']

	# get montly count of all changeset
	mon_co = les_apps.groupby(['user']).resample('M', how='count')[['changeset']] 
	mon_co.columns = ['total_edits']

	# combine unqiue and total edits
	app_mon_total = mon_un.join(mon_co).unstack()

	# output to csv
	app_mon_total.to_csv("montly_app_tracking.csv")