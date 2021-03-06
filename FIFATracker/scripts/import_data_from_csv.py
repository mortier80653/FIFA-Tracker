import os

from django.conf import settings
from django.db import connection

# python manage.py runscript import_data_from_csv --script-args nations20.csv datanations20
# python manage.py runscript import_data_from_csv --script-args playernames20.csv dataplayernames20

# python manage.py runscript import_data_from_csv --script-args nations19.csv datanations19
# python manage.py runscript import_data_from_csv --script-args playernames19.csv dataplayernames19

# python manage.py runscript import_data_from_csv --script-args nations18.csv datanations
# python manage.py runscript import_data_from_csv --script-args playernames18.csv dataplayernames

# python manage.py runscript import_data_from_csv --script-args nations17.csv datanations17
# python manage.py runscript import_data_from_csv --script-args playernames17.csv dataplayernames17


def run(*args):
    fname = args[0]
    table = args[1]

    # FULL PATH TO CSV FILE
    csv_file = os.path.join(settings.BASE_DIR, "..", "Database Data", fname)

    with connection.cursor() as cur:
        with open(csv_file, 'r', encoding='utf-8') as f:
            columns = f.readline()
            SQL_COPY_STATEMENT = """ COPY public.%s (%s) FROM STDIN WITH CSV DELIMITER AS ',' ENCODING 'UTF-8' """
            cur.copy_expert(sql=SQL_COPY_STATEMENT %
                            (table.replace("_", ""), columns), file=f)
            connection.commit()
