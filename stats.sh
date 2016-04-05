#TODAY=date +%Y-%m-%d
TODAY=`date +%Y-%m-%d`

echo "Today is '$TODAY'"

/usr/bin/python3 /home/rustyb/src/leaderboard/get_maplesotho_stats.py --stats

/usr/bin/python3 /home/rustyb/src/leaderboard/since_feb.py

/usr/bin/git add /home/rustyb/src/leaderboard/data

/usr/bin/git commit -am "Updated stats with '$TODAY'"

#git push
