#!/bin/sh

# This script handles this issue: https://github.com/xAranaktu/FIFA-Tracker/issues/9

# comment out "For Release"
sed -i '/firstname = models.ForeignKey/,/Uncomment for migration to fix problem with foreignkeys/s/.*/#&/' players/models.py
# uncomment "migration fix problem with foreignkeys"
sed -i '/firstnameid = models.IntegerField/,/commonnameid = models.IntegerField/s/# //' players/models.py
sleep 1
echo "running migrations fix problem with foreignkeys"

python manage.py makemigrations
python manage.py migrate
sleep 1

# uncomment "For Release"
sed -i '/firstname = models.ForeignKey/,/Uncomment for migration to fix problem with foreignkeys/s/#//' players/models.py
# comment out "migration fix problem with foreignkeys"
sed -i '/firstnameid = models.IntegerField/,/commonnameid = models.IntegerField/s/.*/#&/' players/models.py
sleep 1
echo "running migrations for release"

python manage.py makemigrationsn
python manage.py migrate --fake
