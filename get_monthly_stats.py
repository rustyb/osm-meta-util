# combine stats from geojson.new files located in data/lesotho/.

# import required libraries
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cufflinks as cf
import plotly.plotly as py
import datetime

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
	#
	# get montly count of all changes
	#mon_co = les_apps.groupby(['user']).resample('M', how='count')[['changeset']] 
	#mon_co.columns = ['total_edits']
	#
	# combine unqiue and total edits
	#app_mon_total = mon_un.join(mon_co).unstack()
	# fix for the moment to avoid segmentation fault
	app_mon_total = mon_un
	#
	# output to csv
	app_mon_total.to_csv("montly_app_tracking.csv")
	
	#
	app_yun = les_apps.groupby(['user']).resample('AS', how='nunique')[['changeset']].reset_index().set_index('user')
	app_count = les_apps.groupby(['user']).resample('AS', how='count')[['changeset']].reset_index().set_index('user')
	#
	app_edits = les_apps[['user', 'type']].groupby(['user','type']).size()
	ap_us = app_edits.unstack().fillna(0)
	ap_us['total_edits'] = ap_us['create'] + ap_us['modify'] + ap_us['delete']
	#
	# combine mpaleng users
	mape_users = ['Mpaleng Oliphant', 'Miss O']
	new_tots = ap_us.reset_index()[ap_us.reset_index().user.isin(mape_users)].set_index('user').sum().values
	ap_us.drop(mape_users, inplace=True)
	#
	ap_us = ap_us.reset_index()
	ap_us.loc[len(ap_us)] = list(np.append(['Mpaleng'], new_tots))
	ap_us.set_index('user', inplace=True)
	ap_us[['create', 'delete', 'modify', 'total_edits']] = ap_us[['create', 'delete', 'modify', 'total_edits']].astype('float')
	#reset dtypes to numbers
	ap_us[['total_edits']].sort('total_edits').plot(kind='barh', stacked=True, title="APP Total Edits", figsize=(20,20)).get_figure().savefig('app_total_edits.png')
	ap_us.sort('total_edits')[['create', 'modify', 'delete']].plot(kind='barh', stacked=True, title="APP Edits by Type", figsize=(20,20)).get_figure().savefig('app_edits_by_type.png')
	ap_us.sort('total_edits', ascending=False).to_csv("app_total_edits_by_type.csv")

	
	t = datetime.datetime.now()
	name = ("Users Edits up to  %s-%s-%s" % (t.day, t.month, t.year))
	ap_us.sort('total_edits', ascending=True)[['create', 'delete', 'modify']].iplot(filename="Lesotho Users Edits", title=name, xTitle='Edit Count', kind='barh', barmode='stack', margin=(200,50))
	ranking=ap_us.sort('total_edits', ascending=True)[['create', 'delete', 'modify']].iplot(filename=name, title=name, xTitle='Edit Count', kind='barh', barmode='stack',margin=(200,2,100,50), asFigure=True)
	py.image.save_as(ranking,filename='img/%s' % name,format='png', width=800,height=1000)

# plot timeline to plot.ly
ts = lesa[lesa.index > '2015-01-01'].groupby(['type']).resample('D', how='size').unstack().T
ts.iplot(filename='#MapLesotho Timeline', title='#MapLesotho Timeline', yTitle='Edit Count')

tst = lesa[lesa.user == 'tshedy']
tst = tst.groupby(['type']).resample('D', how='size')
annotations={'2015-03-28':'NUL Mapathon','2015-06-19':'AIT & APP', '2015-04-18': 'Mohales Hoek', '2015-01-15': 'Maseru', '2015-02-13': 'Maseru'}

tst.unstack().T.cumsum().iplot(filename='Tshedy', title='Timeline of Tshedy', yTitle='Edit Count', fill=True, annotations=annotations)

table = ap_us.sort('total_edits', ascending=False).reset_index().to_html()
table = table.replace('border="1"', '')

html_string = '''
<!DOCTYPE html>
<html>
<head>
	<meta charset=utf-8 />
	<title>#MapLesotho Key Stats</title>
	<link href='http://cdn.foundation5.zurb.com/foundation.css' rel='stylesheet' />	
	<style type="text/css">table {border:0;}</style>

	<meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />

	<body>

		<div class="row ">
			<div class="small-12 columns">
				<h2>#MapLesotho User Stats</h2>
				<p>Stats are collected from geofabrik changeset files. Use these graphs to track your progress in the <strong>#MapLesotho</strong> mapping competition with the grand prize of a smartphone curtosy of <a href="https://www.mapillary.com/"><strong>Mapillary</strong></a>.</p>
				<div class="hide-for-small-only">
    			<a href="https://plot.ly/~rustyb/211/" target="_blank" title="Users Edits up to  26-7-2015" style="display: block; text-align: center;"><img src="https://plot.ly/~rustyb/211.png" alt="Users Edits up to  26-7-2015" style="max-width: 100%;"  onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    			<script data-plotly="rustyb:211"  src="https://plot.ly/embed.js" async></script>
				</div>
			</div>
		</div>
		<div class="row show-for-small-only">
			<div class="small-12 columns">
				<p>Graphs will not render properly on this page when on mobile. As such please follow the links below to view graphs.</p>
				<!-- Button Group Optional Classes: [radius round] -->
				<ul class="button-group">
				  <!-- Button Color Classes: [secondary alert success] -->
				  <!-- Button Size Classes: [tiny small large] -->
				  <li><a href="https://plot.ly/~rustyb/211/" class="button">User Bar Graph</a></li>
				  <li><a href="https://plot.ly/~rustyb/148/" class="button">#MapLesotho Timeline Graph</a></li>
				  <li><a href="https://plot.ly/~rustyb/176/" class="button">Tshedy Timeline Graph</a></li>
				</ul>
			</div>
		</div>
		<div class="row hide-for-small-only">
			<div class="small-12 large-6 columns">
				<strong>#MapLesotho Timeline</strong>
				
				   <div>
    					<a href="https://plot.ly/~rustyb/148/" target="_blank" title="#MapLesotho Timeline" style="display: block; text-align: center;"><img src="https://plot.ly/~rustyb/148.png" alt="#MapLesotho Timeline" style="max-width: 100%;"  onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    					<script data-plotly="rustyb:148"  src="https://plot.ly/embed.js" async></script>
					</div>				
			</div>
			<div class="small-12 large-6 columns">
				<strong>Timeline of Tshedy</strong>
				<div>
    				<a href="https://plot.ly/~rustyb/176/" target="_blank" title="Timeline of Tshedy" style="display: block; text-align: center;"><img src="https://plot.ly/~rustyb/176.png" alt="Timeline of Tshedy" style="max-width: 100%;"  onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    				<script data-plotly="rustyb:176"  src="https://plot.ly/embed.js" async></script>
				</div>
			</div>
		</div>
		<div class="row">
			<div class="small-12 columns">
				<strong>#MapLesotho Leaderboard</strong>
				'''+ table + '''			
			</div>
		</div>
	</body>
	</html>
'''
f = open('report.html','w')
f.write(html_string)
f.close()


sys.exit()

ap_us.sort('total_edits')[['create', 'delete', 'modify']].iplot(filename='test 1',kind='barh', barmode='stack', title='#MapLesotho mappers by edits Feb 2015 to 18 July 2015',xTitle='Edits', yTitle='OSM Username')
ap_us.sort('total_edits')[['create', 'delete', 'modify']].iplot(filename='test 1',kind='barh', barmode='stack', title='#MapLesotho mappers by edits Feb 2015 to 18 July 2015',xTitle='Edits', yTitle='OSM Username', colors=['rgba(31, 119, 180, 1)', 'rgba(255, 127, 14, 1)','rgba(44, 160, 44, 1)'], opacity='1',world_readable=True,bargap=0.0, width=0.0)

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

yecapp = les_apps[['user', 'type']].groupby(['user','type']).size().unstack().T
yecapp.apply(f, axis=0).T.plot(kind='barh', stacked=True, title="APP '%' of edit type")

#plot_url = py.plot_mpl(yecapp.unstack().T.apply(f, axis=0).T.plot(kind='barh', stacked=True, title="APP '%' of edit type"))

