# combine stats from geojson.new files located in data/lesotho/.

# import required libraries
from __future__ import print_function
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

import json

import os, sys
import pandas as pd
import numpy as np
import datetime



SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "MapLesothoStats-e1f6b35069cd.json"
SPREADSHEET = "#MapLesotho Validation Challenge - Log your tiles (Responses)"


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

dfiles_h = read_json_files()

leaderbord = pd.DataFrame(columns=['create', 'delete','modify','total_edits'])

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

lesa.set_index(lesa.timestamp, inplace=True)
les_apps = lesa[lesa.index > '27-12-2015']

## get planner stats
apus = pd.read_csv('data/competition_usernames.csv', header=None)
print("Returning stats for %s APPS" % len(apus[1]))
les_apps = lesa[lesa.user.isin(apus[1].values)]


app_edits = les_apps[['user', 'type']].groupby(['user','type']).size()
ap_us = app_edits.unstack().fillna(0)
ap_us['total_edits'] = ap_us.sum(axis=1) 

ap_us = pd.concat([leaderbord.reset_index(), ap_us.reset_index()]).groupby('user').sum()



json_key = json.load(open(SECRETS_FILE))
# Authenticate using the signed key
credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                            json_key['private_key'], SCOPE)

gc = gspread.authorize(credentials)
workbook = gc.open(SPREADSHEET)
# Get the first sheet
sheet = workbook.sheet1

validated = pd.DataFrame(sheet.get_all_records())

column_names = {'Timestamp': 'timestamp','Your username': 'user', 'HotOSM task': 'task', 'Tile Number': 'tile', 'Judge Name': 'judge', 'Agree with validation?': 'validation', '1% Penalty ':'penalty'}
validated.rename(columns=column_names, inplace=True)
validated.timestamp = pd.to_datetime(validated.timestamp)

valid = {'Y':True, 'N': False, '': False}
validated['validation'] = validated['validation'].map(valid)

tcounted = validated[validated['validation'] == True].groupby(['user', 'validation']).size().reset_index()
tcounted.rename(columns = {0:'valid_tiles'}, inplace=True)

tiles_leader = pd.merge(ap_us.reset_index(), tcounted[['user','valid_tiles']], on='user', how='left').set_index('user').sort(['valid_tiles','total_edits'], ascending=False)
tiles_leader.fillna(0, inplace=True)

tiles_leader.reset_index(inplace=True)
min_ts = str(les_apps.index.min())
max_ts = str(les_apps.index.max())

tiles_leader.index = np.arange(1, len(tiles_leader)+1)
new_cols = {'user': 'Username', 'create': 'Created', 'delete': 'Deleted', 'modify': 'Modified', 'total_edit':'Total', 'valid_tiles': 'Tiles'}
tiles_leader.rename(columns=new_cols, inplace=True)
table = pd.DataFrame(tiles_leader).to_html()
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
    <title>#MapLesotho Validation Challenge</title>
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
                <h2>#MapLesotho Validation Challenge</h2>
                <p><a href="./validation.html"><strong>Log your tiles for validation here</strong></a></p>
                <p>Stats are updated once per hour. Your row will turn green once you have 40 of your logged tiles have been validated.</p>
                <p>Full list of Competition Rules</p>
            </div>
        </div>
        
        <div class="row ">
            <div class="small-8 small-centered columns">
                <div class="text-center">
                	<span class="top">'''+ '{:,}'.format(tiles_leader['Tiles'].sum().astype(int)) +'''</span>
                    <span class="top-caption first">total tiles validated since 4 JAN 2016</span>
                    <span class="top minor">'''+ '{:,}'.format(ap_us['total_edits'].sum().astype(int)) +'''</span>
                    <span class="top-caption minor">total since 4 JAN 2016</span>
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
f = open('comp.html','w')
f.write(html_string)
f.close()
