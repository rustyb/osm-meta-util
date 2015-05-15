#!/usr/bin/python

import sys, os, argparse

# take inputs from command line
parser = argparse.ArgumentParser(description='Automatically get OSM Lesotho stats for APPs from geofabrik changesets.')
parser.add_argument('start', help='Start day > 10', type = int)
parser.add_argument('end', help='End day > 10',type = int)
parser.add_argument('--stats', action='store_true', help='Run monthly stats.')

args = parser.parse_args()
start = args.start
end = args.end
stats = args.stats

def check_args(start, end):
	if (start < 10 and end < 10) and (end - start) > -1:
		sys.exit("Both start and end must be large than 10.")
	else:
		print("Checks passed moving one.....\n")


filename = 'lesotho_%s%s.json' % (start, end)
total_files = end - start

print ("Fetching %s changesets from geofabrik...\n" % total_files)
os.system("node examples/cmd.js %s %s | jq -c '{type: .type, user:.user, changeset: .changeset, version: .version, timestamp: .timestamp}' > data/lesotho/%s" % (start, end, filename))
print ("Completed fetch...\n")

print("Converting result into valid JSON...")
os.system(". conv1.sh data/lesotho/%s" % filename)

if stats:
	print("Begin pandas analysis...\n")
	os.system("python get_monthly_stats.py")

