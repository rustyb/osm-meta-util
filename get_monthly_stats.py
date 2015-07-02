# combine stats from geojson.new files located in data/lesotho/.

# import required libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.options.display.mpl_style = 'default' # set styles to nice colours for graphs

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
	
	app_yun = les_apps.groupby(['user']).resample('AS', how='nunique')[['changeset']].reset_index().set_index('user')
	app_count = les_apps.groupby(['user']).resample('AS', how='count')[['changeset']].reset_index().set_index('user')

	app_edits = les_apps[['user', 'type']].groupby(['user','type']).size()
	ap_us = app_edits.unstack().fillna(0)
	ap_us['total_edits'] = ap_us['create'] + ap_us['modify'] + ap_us['delete']

	# combine mpaleng users
	mape_users = ['Mpaleng Oliphant', 'Miss O']
	new_tots = ap_us.reset_index()[ap_us.reset_index().user.isin(mape_users)].set_index('user').sum().values
	ap_us.drop(mape_users, inplace=True)

	ap_us = ap_us.reset_index()
	ap_us.loc[len(ap_us)] = list(np.append(['Mpaleng'], new_tots))
	ap_us.set_index('user', inplace=True)
	ap_us[['create', 'delete', 'modify', 'total_edits']] = ap_us[['create', 'delete', 'modify', 'total_edits']].astype('float')
	#reset dtypes to numbers
	ap_us[['total_edits']].sort('total_edits').plot(kind='barh', stacked=True, title="APP Total Edits", figsize=(20,20)).get_figure().savefig('app_total_edits.png')
	ap_us.sort('total_edits')[['create', 'modify', 'delete']].plot(kind='barh', stacked=True, title="APP Edits by Type", figsize=(20,20)).get_figure().savefig('app_edits_by_type.png')
	ap_us.sort('total_edits', ascending=False).to_csv("app_total_edits_by_type.csv")

sys.exit()

# get some stats for all the users contributing to map_lesotho
yn = lesa.groupby(['user']).resample('AS', how='nunique')[['changeset']].reset_index().set_index('user')
yc = lesa.groupby(['user']).resample('AS', how='count')[['changeset']].reset_index().set_index('user')

yn.columns = ['timestamp', 'number_changesets']
yc.columns = ['timestamp', 'edit_count']

#yec = lesa[['user', 'type']].groupby(['user', 'type']).resample('AS', how='count')[['type']].reset_index().set_index('user')
yec = lesa[['user', 'type']].groupby(['user','type']).size()
yec1 = yec.unstack().fillna(0)
yec1['total_edits'] = yec1.sum(axis=1)
yec1.sort('total_edits', ascending=False).to_csv("all_users_edits_by_type.csv")

## get top 10 users from all
pd.merge(yn[['number_changesets']].reset_index(), yc[['edit_count']].reset_index(), on='user').set_index('user').sort('edit_count', ascending=False)[0:10].plot(kind='barh', title="#MapLesotho Top10 Users - Edits vs Changesets since Feb 2015")

def f(s):
    return s/s.sum()

## get number of creates/modifies/deletes for same top 10
yec1 = yec.reset_index()
ii = pd.merge(yn[['number_changesets']].reset_index(), yc[['edit_count']].reset_index(), on='user').set_index('user').sort('edit_count', ascending=False)[0:10].sort('edit_count', ascending=False).index
xxx =yec.unstack()
xxx.loc[ii.values].T.apply(f, axis=0).T.plot(kind='barh', stacked=True)
xxx.loc[ii.values][['create', 'modify']].plot(kind='barh', stacked=True)


def f(s):
    return s/s.sum()

yecapp = les_apps[['user', 'type']].groupby(['user','type']).size()
yecapp.unstack().T.apply(f, axis=0).T.plot(kind='barh', stacked=True, title="APP '%' of edit type")


