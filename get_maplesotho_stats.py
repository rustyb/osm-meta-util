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
	print "No values given, getting latest sequence number"
	state = requests.get("http://download.geofabrik.de/africa/lesotho-updates/state.txt").content
	seq_num = state.split('\n')[-2].split('=')[-1]
	
	#check that it is 3 long
	if len(seq_num) == 3:
		start = int(seq_num)
		end = int(seq_num)
		print ("Start Number: ", start)
	else:
		print "The sequence number is more than 3 digits long"
		sys.exit()


def check_args(start, end):
	if (start < 10 and end < 10) and (end - start) > -1:
		sys.exit("Both start and end must be large than 10.")
	else:
		print("Checks passed moving one.....\n")


filename = 'lesotho_%s%s.json' % (start, end)
total_files = end - start + 1

print ("Fetching %s changesets from geofabrik...\n" % total_files)
os.system("node examples/cmd.js %s %s | jq -c '{name: .name, type: .type, user:.user, changeset: .changeset, version: .version, timestamp: .timestamp}' > data/lesotho/%s" % (start, end, filename))
print ("Completed fetch...\n")

print("Converting result into valid JSON...")
os.system(". conv1.sh data/lesotho/%s" % filename)

def check_empty_files(files):
    to_delete = ''
    with open(files) as inFile:
        try: 
        	x = json.load(inFile)
        	if x == []:
        		to_delete.append(inFile)
        except ValueError:
        	#x = []
        	print('empty json')
    if len(to_delete) > 0:
	    os.system('rm %s' % to_delete)

jn =  'data/lesotho/' + filename + '.new'
print('JSON FILE: %s' % jn)
check_empty_files(jn)

if stats:
	print("Begin pandas analysis...\n")
	os.system("python get_monthly_stats.py")

