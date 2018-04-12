# FIFA-Tracker
Track your progress in FIFA Career Mode

Try FIFA Tracker now at [https://fifatracker.net/](https://fifatracker.net/)

Development in progress...

# Setup Guide for Windows

**1. Download and install**
- [Python 3.6](https://www.python.org/downloads/)
- [PostgreSQL 10](https://www.postgresql.org/download/windows/)
- [Git](https://git-scm.com/downloads)

**2. Install virtualenv**
```sh
pip install virtualenv
```

**3. Create virtualenv**
```sh
mkdir "C:\Program Files\Project"
cd "C:\Program Files\Project"
virtualenv FT_ENV
```

**4. Activate virtualenv**
```sh
cd "FT_ENV\Scripts"
activate.bat
```

**5. Clone FIFA Tracker repository**
```sh
cd "..\.."
git clone https://github.com/xAranaktu/FIFA-Tracker.git
```

**6. Install dependencies**
```sh
pip install -r "FIFA-Tracker\requirements.txt"
```

**7. Create ["secret_settings.py"](https://gist.github.com/xAranaktu/c4c954ac249472d541aff36ecce9bf12) file in "FIFATracker\Fifa_Tracker" dir**

![secret_settings](https://i.imgur.com/MBPIeYQ.png)

**Note** Make sure that database name and password is correct.

**8. Database migrations**

It's awkward because you cannot store a null primary key in PostgreSQL database which is surprisingly possible in FIFA Database.

```sh
cd "FIFA-Tracker\FIFATracker"
python manage.py migrate players 0001
python manage.py migrate --fake players 0002
python manage.py migrate
```

**9. Populate Database**

"playernames" & "nations" tables are not included in career save. So you need to populate these tables from .csv files.
Just simply navigate to your PostrgreSQL\bin folder and execute proper commands or use pgAdmin.

Commands examples:

```sh
psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames (name,nameid,commentaryid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames.csv' delimiter ',' csv header ENCODING 'UTF8';"
```

```sh
psql -d FIFA_TRACKER --username=postgres -c "COPY dataplayernames17 (name,commentaryid,nameid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\playernames17.csv' delimiter ',' csv header ENCODING 'UTF8';"
```

```sh
psql -d FIFA_TRACKER --username=postgres -c "COPY datanations (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid) FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations.csv' delimiter ',' csv header ENCODING 'UTF8';"
```

```sh
psql -d FIFA_TRACKER --username=postgres -c "COPY datanations17 (isocountrycode,nationname,confederation,top_tier,nationstartingfirstletter,groupid,nationid)  FROM 'C:\Program Files\Project\FIFA-Tracker\Database Data\nations17.csv' delimiter ',' csv header ENCODING 'UTF8';"
```

**10. Run server**

Make sure virtualenv is still active. Then change dir to "FIFA-Tracker\FIFATracker" and run django server.

```sh
python manage.py runserver
```

Your local FIFA Tracker project will be available at **127.0.0.1:8000**.