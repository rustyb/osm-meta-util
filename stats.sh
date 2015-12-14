#TODAY=date +%Y-%m-%d
TODAY=`date +%Y-%m-%d`

echo "Today is '$TODAY'"

/usr/bin/python3 /home/rustyb/src/leaderbord/get_maplesotho_stats.py --stats

/usr/bin/git add /home/rustyb/src/leaderboard/data

/usr/bin/git commit -am "Updated stats with '$TODAY'"

#git push
