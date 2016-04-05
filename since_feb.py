# combine stats from geojson.new files located in data/lesotho/.

# import required libraries
import os, sys
import pandas as pd
import numpy as np
import datetime

from sqlalchemy import create_engine
engine = create_engine("sqlite:///db/leaderboard4.db", echo=False, convert_unicode=True)

xx = pd.read_sql("SELECT user, type, count(*) as edit_count from changesets where timestamp >= '2016-02-20 00:00:00' group by user, type order by user", engine)
edits = xx.groupby(['type', 'user']).sum().unstack().T
ap_us = edits.reset_index().set_index('user')[['create', 'delete', 'modify']].fillna(0)

ap_us['total_edits'] = ap_us.sum(axis=1) 

act = pd.read_sql("select user, max(timestamp) as last_act from changesets group by user order by user", engine, parse_dates=['last_act'])
act['days_since'] = (pd.datetime.now() - act.last_act).dt.days
act2 = act[['user', 'days_since']]

act2 = act2.rename(columns={ 'days_since' : 'days since last edit'})

total_rank = ap_us.sort('total_edits', ascending=False).reset_index()
final = pd.merge(total_rank, act2, how='left', on=['user'])


min_ts = 'test'#str(les_apps.index.min())
max_ts = 'test'#str(les_apps.index.max())

final.index = np.arange(1, len(final)+1)
table = pd.DataFrame(final).to_html()
table = table.replace('border="1"', '')

table = table.replace('<table  class="dataframe">', '<table class="dataframe" align="center">')
table = table.replace('<th></th>', '<th>Rank</th>')
table = table.replace('<th>changeset</th>', '<th>Total Edits</th>')

#leaderboard = ap_us

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
                <h2>#MapLesotho - <strong>Since the beardies left</strong></h2>
            </div>
        </div>
        
        <div class="row ">
            <div class="small-8 small-centered columns">
                <div class="text-center">
                    <span class="top">'''+ '{:,}'.format(ap_us['total_edits'].sum().astype(int)) +'''</span>
                    <span class="top-caption first">total since 20 FEB 2016</span>
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
f = open('since_feb.html','w')
f.write(html_string)
f.close()
