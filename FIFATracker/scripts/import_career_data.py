import os
from django.db import connection


def run(*args):
    """ Populate data in table with content from csv file """
    csv_path = args[0]
    tables = args[1]

    if tables:
        tables = tables.split(',')

    with connection.cursor() as cur:
        for csv in tables:
            if csv[-2:].isdigit():
                full_csv_path = os.path.join(csv_path, csv[:-2]) + ".csv"
            else:
                full_csv_path = os.path.join(csv_path, csv) + ".csv"

            with open(full_csv_path, 'r', encoding='utf-8') as f:
                columns = f.readline()
                SQL_COPY_STATEMENT = """ COPY public.%s (%s) FROM STDIN WITH CSV DELIMITER AS ',' ENCODING 'UTF-8' """
                cur.copy_expert(
                    sql=SQL_COPY_STATEMENT % ("datausers{}".format(csv.replace("_", "")), columns),
                    file=f
                )
                connection.commit()
