node examples/cmd.js 50 80 10000 | jq -c '{user:.user, changeset: .changeset, version: .version, timestamp: .timestamp}' > lesotho4980.json

awk '{print $0","}' lesotho1649.json > lesotho11649.json

. conv1.sh lesotho.json
"outputs lesotho.json.new with [...]"

## python

import pandas as pd
import numpy as np

les = pd.read_json('lesotho11649.json')
les = pd.read_json('lesotho4980_1_copy.json.new')
les.timestamp = pd.to_datetime(les['timestamp']) # convert timestamp to date time index
les.set_index(les.timestamp, inplace=True)


results = les.groupby(['user', 'changeset']).size()
results = les.groupby(['user']).size()

# set a new column that contains the weekday
````
les['day'] = les.index.weekday

results = les.groupby(['user', 'day']).size()

res = les.groupby(['user', 'day']).changeset.nunique()
res.unstack

res = les.groupby(['day', 'user']).changeset.nunique().unstack()
res1 = res.transpose()
````
# rename the columns to make some sense
```
res1.columns = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
```

```
res1.describe
```

add a total column

```
res1['total'] = res1.sum(axis=1)
```

# output to text file to display on punchcard
````res1.reset_index().to_csv('les_data.csv', encoding='utf-8', index=False, na_rep=0)````

# filter out only app results
file is located at apps/app_unames.csv

````
apus = pd.read_csv('apps/app_unames.csv')
apps = apus.username[apus.is_app == 'Y']
app_edits = les[les.user.isin(apps.values)]
app_edits.timestamp = pd.to_datetime(app_edits['timestamp']) # convert timestamp to date time index
app_edits.set_index(app_edits.timestamp, inplace=True)

app_results = app_edits.groupby(['user']).agg()
````

# get time series of daily create delete update...
ts = test1.groupby(['type']).resample('D', how='size')
ts = lesa[lesa.index > '2015-01-01'].groupby(['type']).resample('D', how='size')
ts.unstack().T.iplot(filename='#MapLesotho Timeline', title='#MapLesotho Timeline', yTitle='Edit Count')

tst.iplot(filename='#MapLesotho Timeline', title='#MapLesotho Timeline', yTitle='Edit Count', fill=True)

annotations={'2015-03-28':'NUL Mapathon','2015-06-19':'AIT & APP','2015-06-18':'Pioneer Mall', '2015-04-18': 'Mohales Hoek', '2015-01-15': 'Maseru', '2015-02-13': 'Maseru'}

tst[['create', 'delete','modify']].iplot(filename='#MapLesotho Timeline', title='#MapLesotho Timeline', yTitle='Edit Count', fill=True, annotations=annotations)

tst.iplot(filename='#MapLesotho Timeline', title='#MapLesotho Timeline', yTitle='Edit Count', fill=True, annotations=annotations)

tst = lesa[lesa.user == 'tshedy']
tst = tst.groupby(['type']).resample('D', how='size')
tst.unstack().T.cumsum().iplot(filename='Tshedy', title='Timeline of Tshedy', yTitle='Edit Count', fill=True)

sss = ap_us.sort('total_edits', ascending=True)[['create', 'delete', 'modify']].iplot(filename=name, title=name, xTitle='Edit Count', kind='barh', barmode='stack', asFigure=True, dimensions=(500,1000), margin=(200,2,2,2))

py.image.save_as(sss,filename='img/test.png',format='png', width=500,height=1000)

