#!/usr/bin/python

import sys, os, argparse, requests, json

# take inputs from command line
parser = argparse.ArgumentParser(description='Automatically get OSM Lesotho stats for APPs from geofabrik changesets.')
parser.add_argument('start', help='Start day > 10', type = int, nargs='?')
parser.add_argument('end', help='End day > 10',type = int, nargs='?')
parser.add_argument('--stats', action='store_true', help='Run monthly stats.')

args = parser.parse_args()
start = args.start
end = args.end
stats = args.stats

if (start or end) == None:
	print("No values given, getting latest sequence number")
	# 
	state = requests.get("http://planet.openstreetmap.org/replication/hour/state.txt").text
	seq_num = state.split('\n')[1].split('=')[-1]
	
	#check that it is 3 long
	if len(seq_num) >= 3:
		start = int(seq_num)
		end = int(seq_num)
		print ("Start Number: ", start)
	else:
		print("The sequence number is more than 3 digits long")
		sys.exit()


def check_args(start, end):
	if (start < 10 and end < 10) and (end - start) > -1:
		sys.exit("Both start and end must be large than 10.")
	else:
		print("Checks passed moving one.....\n")


filename = 'lesotho_%s_%s.json' % (start, end)
total_files = end - start + 1

print ("Fetching %s changesets from geofabrik...\n" % total_files)
os.system("/home/rustyb/.nvm/versions/node/v4.2.2/bin/node examples/cmd.js %s %s | jq -s '[. | .[] | select(.lat != null or .lon != null) | {user: .user, id: .id|tonumber, version: .version|tonumber, lat: .lat|tonumber, lon: .lon|tonumber, timestamp:.timestamp, type: .type, name: .name} | select(.lat >=-30.751277776257812 and .lat <= -28.53144 and .lon >= 26.74072265625 and .lon <= 29.498291015624996)]' > data/lesotho1/%s" % (start, end, filename))
print ("Completed fetch...\n")

#print("Converting result into valid JSON...")
#os.system(". conv1.sh data/lesotho/%s" % filename)
def check_empty_files(files):
    to_delete = ''
    with open(files) as inFile:
        try: 
        	x = json.load(inFile)
        	if x == []:
        		to_delete += files
        except ValueError:
        	#x = []
        	print('empty json')
    if len(to_delete) > 0:
	    os.system('rm %s' % to_delete)

jn =  './data/lesotho1/' + filename
print('JSON FILE: %s' % jn)
#check_empty_files(jn)


###### add file to db
from datetime import datetime
import os, sys, json

from sqlalchemy import create_engine
engine = create_engine("sqlite:///db/leaderboard2.db", echo=False, convert_unicode=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker(bind=engine)

from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String



class Changeset(Base):
    __tablename__ = "changesets"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    timestamp = Column(DateTime)
    lon = Column(Float)
    lat = Column(Float)
    version = Column(Integer)
    user = Column(String)	



session = DBSession()
with open(jn) as json_file:
	json_data = json.load(json_file)
	print('Adding %s to db' % jn)
	for i in json_data:
	    if 'name' in i:
	        name = i['name']
	    else:
	        name = 'node'
	    if 'lat' in i:
	        lat = i['lat']
	        lon = i['lon']
	    else:
	        lat = None
	        lon = None
	    session.merge(Changeset(id=i['id'], name=name, type=i['type'], timestamp=datetime.strptime(i['timestamp'], "%Y-%m-%dT%H:%M:%SZ"), user = i['user'], lat=lat, lon=lon, version=i['version']))   
	session.commit()



if stats:
	print("Begin pandas analysis...\n")
	os.system("/usr/bin/python3 get_monthly_stats.py")

