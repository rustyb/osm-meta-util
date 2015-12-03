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
def read_files(place="lesotho"):
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
    

dfiles = read_files()

les0 = []
for f in dfiles:
    les0.append(pd.read_json(f))


lesa = pd.concat(les0)
print("Dataframe with %s rows x %s columns" % (lesa.shape[0], lesa.shape[1]))

lesa.timestamp = pd.to_datetime(lesa['timestamp']) # convert timestamp to date time index
# data cleaning, set all 'Miss O' to 'Mpaleng Oliphant'
#lesa.replace(['Miss O', 'The Big C'], ['Mpaleng Oliphant', 'DeBigC'], inplace=True)

lesa.set_index(lesa.timestamp, inplace=True)

## get planner stats
#apus = pd.read_csv('data/lesotho/app_unames.csv')
#apps = apus.username[apus.is_app == 'Y']

#print("Returning monthly stats for %s Assistant Planners" % len(apps))
#les_apps = lesa[lesa.user.isin(apps.values)]
#les_apps.drop('name', axis=1, inplace=True) # drop column with name: [way,node]
#les_apps = les_apps[les_apps['name'] != 'way'] # remove all the ways
les_apps = lesa.rename(columns = {'id':'changeset'})
min_ts = str(les_apps.index.min())
max_ts = str(les_apps.index.max())
total = les_apps.groupby(['user']).resample('A', how='count')[['changeset']].reset_index()
total_rank = pd.DataFrame(total[['user','changeset']]).sort('changeset', ascending=False)
total_rank.index = np.arange(1, len(total_rank)+1)
table = pd.DataFrame(total_rank).to_html()
table = table.replace('border="1"', '')

table = table.replace('<table  class="dataframe">', '<table class="dataframe" align="center">')
table = table.replace('<th></th>', '<th>Rank</th>')
table = table.replace('<th>changeset</th>', '<th>Total Edits</th>')


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
    </style>
    <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />
    <body>
        <div class="row text-center">
            <div class="small-8 small-centered columns text-center">
                <h2>#MapLesotho Portmarnock CS 24H Mapathon</h2>
                <p>These stats are updated once per hour. Use the table to track your ranking througout the mapathon.</a>.</p>
            </div>
        </div>
        
        <div class="row ">
            <div class="small-8 small-centered columns">
                <div class="text-center">
                    <strong>#MapLesotho Portmarnock 24H Leaderboard</strong>
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
