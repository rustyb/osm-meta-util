# combine stats from geojson.new files located in data/lesotho/.

# import required libraries
import os, sys
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import cufflinks as cf
#import plotly.plotly as py
import datetime

#pd.options.display.mpl_style = 'default' # set styles to nice colours for graphs

# read files in data folder for existing files:
def read_json_files(place="lesotho"):
    wd0 = 'data/'
    if place == 'lesotho':
        wd = wd0 + 'lesotho1/'
    else:
        wd = wd0
    files = os.listdir (wd) # from /src
    fcheck = any (f.find ("lesotho") > -1 and f.endswith(".json") for f in files)
    if fcheck:
        json_files = [wd + i for i in files if i.endswith('.json')]
        print('Found %s geojson.new files in directory...' % len(json_files))
        return json_files
    else:
        #sys.exit("make sure that json.new files exist in the data/lesotho directory.")
        print("fcheck failes")

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
    

dfiles_h = read_json_files()
dfiles_d = read_files() # read old daily


leaderbord = pd.DataFrame(columns=['create', 'delete','modify','total_edits'])

for f in dfiles_d:
    print('PRINTING: ' + f)
    lesa = pd.read_json(f);
    lesa.timestamp = pd.to_datetime(lesa['timestamp']) # convert timestamp to date time index
    lesa.set_index(lesa.timestamp, inplace=True)
    les_apps = lesa[lesa.index > '01-01-2015']
    app_edits = les_apps[['user', 'type']].groupby(['user','type']).size()
    ap_us = app_edits.unstack().fillna(0)
    #ap_us['total_edits'] = ap_us['create'] + ap_us['modify'] + ap_us['delete']  
    ap_us['total_edits'] = ap_us.sum(axis=1)
    leaderbord = pd.concat([leaderbord.reset_index(), ap_us.reset_index()]).groupby('user').sum()



les_hourly = []
for f in dfiles_h:
    les_hourly.append(pd.read_json(f))

lesh = pd.concat(les_hourly)
# fix the naming of columns so they're the same
lesh = lesh.rename(columns = {'id':'changeset'})
#lesd = pd.concat(les_daily)

lesa = lesh
print("Dataframe with %s rows x %s columns" % (lesa.shape[0], lesa.shape[1]))

lesa.timestamp = pd.to_datetime(lesa['timestamp']) # convert timestamp to date time index
# data cleaning, set all 'Miss O' to 'Mpaleng Oliphant'
#lesa.replace(['Miss O', 'The Big C'], ['Mpaleng Oliphant', 'DeBigC'], inplace=True)

lesa.set_index(lesa.timestamp, inplace=True)
les_apps = lesa[lesa.index > '01-01-2015']
## get planner stats
#apus = pd.read_csv('data/lesotho/app_unames.csv')
#apps = apus.username[apus.is_app == 'Y']

app_edits = les_apps[['user', 'type']].groupby(['user','type']).size()
ap_us = app_edits.unstack().fillna(0)
ap_us['total_edits'] = ap_us.sum(axis=1) 

ap_us = pd.concat([leaderbord.reset_index(), ap_us.reset_index()]).groupby('user').sum()


total_rank = ap_us.sort('total_edits', ascending=False).reset_index()
#print("Returning monthly stats for %s Assistant Planners" % len(apps))
#les_apps = lesa[lesa.user.isin(apps.values)]
#les_apps.drop('name', axis=1, inplace=True) # drop column with name: [way,node]
#les_apps = les_apps[les_apps['name'] != 'way'] # remove all the ways
#les_apps = lesa.rename(columns = {'id':'changeset'})
min_ts = str(les_apps.index.min())
max_ts = str(les_apps.index.max())
#total = les_apps.groupby(['user']).resample('A', how='count')[['changeset']].reset_index()
#total_rank = pd.DataFrame(total[['user','changeset']]).sort('changeset', ascending=False)
total_rank.index = np.arange(1, len(total_rank)+1)
table = pd.DataFrame(total_rank).to_html()
table = table.replace('border="1"', '')

table = table.replace('<table  class="dataframe">', '<table class="dataframe" align="center">')
table = table.replace('<th></th>', '<th>Rank</th>')
table = table.replace('<th>changeset</th>', '<th>Total Edits</th>')

leaderboard = ap_us

html_string = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset=utf-8 />
    <title>#MapLesotho - Portmarnock Mapathon</title>
    <link href='https://cdnjs.cloudflare.com/ajax/libs/foundation/6.0.1/css/foundation.min.css' rel='stylesheet' /> 
    <style type="text/css">
    table {border:0;}
    /*.dataframe tbody tr:nth-child(-n+10){
    background-color: #43AC6A;
    }*/
    .row {max-width:72rem;}
    /*.dataframe tbody tr:nth-child(-n+10) td{color:#fff; font-weight: bold;}*/
    .dataframe tbody tr th {
    text-align: right;
    }
    /*.dataframe tbody tr:nth-child(-n+10) th {
    color: #FFF;
    }*/
    .top-caption {
        font-size: 16px;
        line-height: 1.25;
        font-weight: 400;
        text-transform: uppercase;
        padding-top: 5px;
        padding-bottom: 5px;
        display: block;
        padding-bottom: 30px;
    }
    span.top {
        font-size: 3.5em;
        font-weight: 600;
        display: block;
        clear: both;
        line-height: 1;
    }
    .top.minor, .top-caption.minor {
        font-size: 16px;
        display: inline-block;
        text-transform: capitalize;
    }
    .top-caption.first {
        padding-bottom: 0;
    }
    </style>
    <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />
    <body>
        <div class="row text-center">
            <div class="small-8 small-centered columns text-center">
                <h2>#MapLesotho - Numbers tracker</h2>
                <p>These stats are updated once per hour. Use the table to track your ranking based on such an abritary thing,<br>simple the number of edits you've maded.</p>
            </div>
        </div>
        
        <div class="row ">
            <div class="small-8 small-centered columns">
                <div class="text-center">
                    <span class="top">'''+ '{:,}'.format(ap_us['total_edits'].sum().astype(int)) +'''</span>
                    <span class="top-caption first">total since 1 FEB 2015</span>
                    <span class="top minor">'''+ '{:,}'.format(ap_us['create'].sum().astype(int)) +'''</span>
                    <span class="top-caption minor">created</span>
                    <span class="top minor">'''+ '{:,}'.format(ap_us['modify'].sum().astype(int)) +'''</span>
                    <span class="top-caption minor">modified</span>
                    <span class="top minor ">'''+ '{:,}'.format(ap_us['delete'].sum().astype(int)) +'''</span>
                    <span class="top-caption minor">created</span>
                    <br> <small>First Edit Counted: '''+ min_ts +'''</small>
                    <br> <small>Latest Edit Counted: '''+ max_ts +'''</small>
                </div>
                '''+ table + '''            
            </div>
        </div>
    </body>
    </html>
'''
f = open('index.html','w')
f.write(html_string)
f.close()
