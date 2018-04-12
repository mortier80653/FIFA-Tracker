"playernames" & "nations" tables are not included in career save.
You can use these .csv files to populate your database.

Just simply navigate to your PostrgreSQL\bin folder and execute proper commands.
Commands example:

psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames (name,nameid,commentaryid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames17 (name,commentaryid,nameid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames17.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY datanations (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY datanations17 (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid)  FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations17.csv' delimiter ',' csv header ENCODING 'UTF8';"