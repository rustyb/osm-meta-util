#TODAY=date +%Y-%m-%d
TODAY=`date +%Y-%m-%d`

echo "Today is '$TODAY'"

python3 get_maplesotho_stats.py --stats

git add data

git commit -am "Updated stats with '$TODAY'"

#git push