#!/usr/bin/python

import os, argparse

# take inputs from command line
parser = argparse.ArgumentParser(description='Automatically get OSM Lesotho stats for APPs from geofabrik changesets.')
parser.add_argument('start', help='Start day > 10', type = int)
parser.add_argument('end', help='End day > 10',type = int)

args = parser.parse_args()
start = args.start
end = args.end

def check_args(start, end):
	if (start < 10 and end < 10) and (end - start) > -1:
		sys.exit("Both start and end must be large than 10.")
	else:
		print("Checks passed moving one.....\n")


filename = 'lesotho_%s%s.json' % (start, end)

print ("Fetching the changesets from geofabrik...\n")
os.system("node examples/cmd.js %s %s 30000 | jq -c '{type: .type, user:.user, changeset: .changeset, version: .version, timestamp: .timestamp}' > data/lesotho/%s" % (start, end, filename))
print ("Completed fetch...\n")

print("Converting result into valid JSON...")
os.system(". conv1.sh data/lesotho/%s" % filename)

print("Begin pandas analysis...\n")

# import libraries
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
	else:
		sys.exit("make sure that json.new files exist in the data/lesotho directory.")
	return json_files

dfiles = read_files()

les0 = []
for f in dfiles:
	les0.append(pd.read_json(f))


lesa = pd.concat(les0)

lesa.timestamp = pd.to_datetime(lesa['timestamp']) # convert timestamp to date time index
lesa.set_index(lesa.timestamp, inplace=True)

apus = pd.read_csv('data/lesotho/app_unames.csv')
apps = apus.username[apus.is_app == 'Y']

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