"playernames" & "nations" tables are not included in career save.
You can use these .csv files to populate your database.

Just simply navigate to your PostrgreSQL\bin folder and execute proper commands.
Commands example:

psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames20 (name,nameid,commentaryid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames20.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames19 (name,nameid,commentaryid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames19.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames18 (name,nameid,commentaryid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames18.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames17 (name,nameid,commentaryid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames17.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY datanations20 (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations20.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY datanations19 (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations19.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY datanations18 (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations18.csv' delimiter ',' csv header ENCODING 'UTF8';"

psql -d FIFA_TRACKER --username=postgres -c "COPY datanations17 (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid)  FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations17.csv' delimiter ',' csv header ENCODING 'UTF8';"
