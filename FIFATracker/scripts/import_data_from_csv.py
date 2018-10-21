import os

from django.conf import settings
from django.db import connection

# python manage.py runscript import_data_from_csv --script-args nations19.csv datanations19
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
